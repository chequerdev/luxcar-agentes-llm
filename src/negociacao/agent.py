"""Seleção de ferramenta pelo modelo, decisão comercial e confirmação pelo código."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import time
import unicodedata
import uuid

from .store import DataError, Store, read_rows

ROOT = Path(__file__).resolve().parents[2]
PROMPT = ROOT / "prompts/luxcar-v1.md"
MAX_STEPS = 5
INPUT_ALLOWANCE = 7500
OUTPUT_ALLOWANCE = 512
MAX_BYTES = 512
MODEL = "openai/gpt-oss-20b"
BASE_URL = "https://api.groq.com/openai/v1"
NAMES = ("consultar_estoque", "registrar_proposta", "encaminhar")


def schema(name, properties):
    return {"type": "function", "function": {
        "name": name,
        "description": {"consultar_estoque": "Consulta disponibilidade sem gravar",
                        "registrar_proposta": "Solicita revisão humana de proposta; sem confirmação não registra",
                        "encaminhar": "Solicita esclarecimento ou encerra fora do escopo"}[name],
        "parameters": {"type": "object", "properties": properties, "required": list(properties),
                       "additionalProperties": False},
    }}


TOOLS = [
    schema(NAMES[0], {"veiculo_id": {"type": "integer"}}),
    schema(NAMES[1], {"veiculo_id": {"type": "integer"}, "valor_centavos": {"type": "integer"}}),
    schema(NAMES[2], {"motivo": {"type": "string", "enum": ["dados_insuficientes", "divergencia", "fora_de_escopo"]}}),
]
CATALOG_FIELDS = {"id": int, "marca": str, "modelo": str, "ano": int, "versao": str}
RESPONSES = {
    "elegivel": "Veículo disponível para negociação. Nenhuma proposta registrada.",
    "negociacao_ativa": "Já há uma proposta ativa para o veículo. Encaminhe ao gerente comercial.",
    "veiculo_indisponivel": "Veículo indisponível. Nenhuma proposta criada.",
    "veiculo_inexistente": "Veículo não encontrado no catálogo. Confirme o ID com o responsável pelo estoque.",
    "abaixo_do_minimo": "Valor abaixo do mínimo. Encaminhe ao gerente comercial, sem registrar.",
    "aguardando_confirmacao": "Revise veículo e valor. Confirme ou rejeite usando o ID da revisão.",
    "gravada": "Proposta registrada.",
    "ja_registrada": "Proposta já registrada. Nenhuma duplicata criada.",
    "rejeitada": "Revisão rejeitada. Nenhuma proposta criada.",
    "revisao_nao_encontrada": "Revisão não encontrada para este vendedor.",
    "confirmacao_expirada": "Revisão expirada. Abra uma nova revisão se necessário.",
    "dados_insuficientes": "Informe um único veículo e, para abrir proposta, o valor em reais.",
    "divergencia": "Os dados não identificam um pedido único. Confirme veículo, valor e intenção.",
    "fora_de_escopo": "O agente consulta disponibilidade e revisa abertura de propostas.",
    "erro_dados": "Fonte indisponível ou inválida. Encaminhe ao responsável pelo estoque. Nenhuma proposta criada.",
    "erro_modelo": "Não foi possível validar a seleção do modelo. Nenhuma proposta criada.",
    "limite_tokens": "Orçamento da chamada excedido. Nenhuma proposta criada.",
    "limite_passos": "Limite de passos atingido. Nenhuma proposta criada.",
    "entrada_invalida": "Forneça uma mensagem curta e um identificador fictício de vendedor.",
}


def normalized(text):
    return "".join(c for c in unicodedata.normalize("NFKD", text.lower()) if not unicodedata.combining(c))


def extract(text, rows):
    """Referência determinística. Escrita exige concordância entre modelo e dados explícitos."""
    query = normalized(text)
    def refer(pattern):
        return re.search(r"\b(?:" + pattern + r")\b", query)

    def route(reason):
        return NAMES[2], {"motivo": reason}

    writing = re.search(r"\b(?:abra|abre|abrir|registre|registrar|crie|criar)\s+(?:(?:uma|a|nova)\s+)*(?:proposta|negociacao)\b", query)
    reading = refer("disponivel|disponibilidade|estoque|status")
    if not (writing or reading):
        return route("fora_de_escopo")
    if (writing and (reading or refer("nao|sem|cancele|cancelar|se|talvez"))) or refer("ou|mas"):
        return route("divergencia")
    ids = set(int(i) for i in re.findall(r"\b(?:id|veiculo)\s*#?\s*(\d{1,9})\b", query))
    named = [row for row in rows if re.search(r"\b" + re.escape(normalized(row["modelo"])) + r"\b", query)]
    ids.update(row["id"] for row in named)
    brands = {normalized(row["marca"]) for row in rows
              if re.search(r"\b" + re.escape(normalized(row["marca"])) + r"\b", query)}
    years_query = re.sub(r"r\$\s*[\d.,]+", "", query)
    if len(ids) > 1:
        return route("divergencia")
    years = set(re.findall(r"\b(?:19|20)\d{2}\b", years_query))
    if any((years and years != {str(row["ano"])}) or
           (brands and brands != {normalized(row["marca"])})
           for row in rows if row["id"] in ids):
        return route("divergencia")
    if not ids:
        return route("dados_insuficientes")
    args = {"veiculo_id": ids.pop()}
    if not writing:
        return NAMES[0], args
    amounts = re.findall(r"r\$\s*(\d{1,3}(?:\.\d{3})+(?:,\d{2})?|\d{1,9}(?:,\d{2})?)(?![\d.,])", query)
    if len(amounts) != 1:
        return route("divergencia" if len(amounts) > 1 else "dados_insuficientes")
    integer, _, decimals = amounts[0].replace(".", "").partition(",")
    value = 100 * int(integer) + int(decimals or "0")
    if not 0 < value <= 100_000_000_00:
        return route("dados_insuficientes")
    return NAMES[1], {**args, "valor_centavos": value}


@dataclass
class Run:
    mode: str
    model: str | None
    case: str | None
    run_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    events: list = field(default_factory=list)
    tokens: dict = field(default_factory=lambda: {"entrada": 0, "saida": 0})
    prompt_hash: str | None = None

    def step(self, name, **data):
        if len(self.events) >= MAX_STEPS:
            raise AgentError("limite_passos")
        self.events.append({"passo": len(self.events) + 1, "etapa": name, **data})


class AgentError(Exception):
    pass


class Agent:
    def __init__(self, store, logfile, *, mode="local", model=MODEL, client=None):
        self.store, self.logfile, self.mode, self.model, self.client = store, logfile, mode, model, client

    def select(self, text, rows, run):
        prompt = PROMPT.read_text(encoding="utf-8")
        run.prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
        reference = extract(text, rows)
        if self.mode == "local":
            run.step("roteamento", decide="codigo", ferramenta=reference[0], argumentos=reference[1])
            return reference
        messages = [{"role": "system", "content": prompt + "\nCatálogo: " + json.dumps(rows, ensure_ascii=False)},
                    {"role": "user", "content": text}]
        reserved = len(json.dumps([messages, TOOLS], ensure_ascii=False).encode()) + 256
        if reserved > INPUT_ALLOWANCE:
            raise AgentError("limite_tokens")
        start = time.perf_counter()
        try:
            # Técnica: instruções de sistema + function calling. Contrato: uma
            # ferramenta com argumentos tipados. Impede saída livre virar escrita
            # ou autorização; a proposta ainda passa por validação e revisão.
            response = self.client.chat.completions.create(
                model=self.model, temperature=0, max_completion_tokens=OUTPUT_ALLOWANCE,
                messages=messages, tools=TOOLS, tool_choice="required")
            usage = response.usage
            if usage is None:
                raise AgentError("erro_modelo")
            run.tokens = {"entrada": usage.prompt_tokens, "saida": usage.completion_tokens}
            run.step("modelo", decide="modelo", latencia_ms=round((time.perf_counter() - start) * 1000),
                     response_id=response.id, reserva_entrada=reserved)
            if usage.prompt_tokens > INPUT_ALLOWANCE or usage.completion_tokens > OUTPUT_ALLOWANCE:
                raise AgentError("limite_tokens")
            choice = response.choices[0]
            calls = choice.message.tool_calls or []
            if choice.finish_reason != "tool_calls" or len(calls) != 1:
                raise AgentError("erro_modelo")
            chosen = calls[0].function.name, json.loads(calls[0].function.arguments)
            run.events[-1]["ferramenta"] = chosen[0] if chosen[0] in NAMES else "desconhecida"
            if chosen[0] not in NAMES or not isinstance(chosen[1], dict):
                raise AgentError("erro_modelo")
            if chosen[0] == NAMES[2] and chosen[1] in [
                {"motivo": "dados_insuficientes"}, {"motivo": "divergencia"}, {"motivo": "fora_de_escopo"}
            ]:
                return chosen  # O modelo pode recusar uma ação, nunca ampliar a autorização.
            if (chosen != reference or any(type(v) is not int for v in chosen[1].values())):
                raise AgentError("erro_modelo")
            return chosen
        except AgentError:
            raise
        except Exception as err:
            raise AgentError("erro_modelo", type(err).__name__) from err

    def execute(self, seller, *, text=None, review=None, approval=None, case=None):
        started = time.perf_counter()
        run = Run(self.mode if review is None else "confirmacao_humana",
                  self.model if review is None and self.mode == "llm" else None, case)
        try:
            run.step("entrada", decide="codigo")
            if not isinstance(seller, str) or not re.fullmatch(r"[a-zA-Z][a-zA-Z0-9_-]{0,31}", seller):
                raise AgentError("entrada_invalida")
            if review is not None:
                if text is not None or not re.fullmatch(r"[a-f0-9]{32}", review) or type(approval) is not bool:
                    raise AgentError("entrada_invalida")
                run.step("confirmacao", decide="humano", resposta="sim" if approval else "nao")
                run.step("registrar_proposta", decide="codigo")
                data = self.store.resolve(seller, review, approval)
            else:
                if not isinstance(text, str) or not text.strip() or len(text.encode()) > MAX_BYTES:
                    raise AgentError("entrada_invalida")
                rows = [{k: row[k] for k in CATALOG_FIELDS} for row in read_rows(self.store.catalog, CATALOG_FIELDS)]
                name, args = self.select(text, rows, run)
                run.step(name, decide="codigo", argumentos=args)
                if name == NAMES[0]:
                    vehicle, reason = self.store.consult(args["veiculo_id"])
                    data = {"motivo": reason, "veiculo": vehicle}
                elif name == NAMES[1]:
                    data = self.store.prepare(seller, args["veiculo_id"], args["valor_centavos"])
                else:
                    data = args
            run.events[-1]["resultado"] = data["motivo"]
        except (AgentError, DataError, OSError, sqlite3.Error) as err:
            reason = err.args[0] if isinstance(err, AgentError) else "erro_dados"
            event = {"erro": reason}
            if isinstance(err, DataError):
                event["detalhe"] = str(err)
            elif isinstance(err, AgentError) and len(err.args) > 1:
                event["detalhe"] = err.args[1]
            run.events[-1].update(event)
            data = {"motivo": reason}

        reason = data["motivo"]
        output = {"execucao_id": run.run_id, **data, "mensagem": RESPONSES[reason]}
        record = {
            "schema": "luxcar.negociacao.v1", "execucao_id": run.run_id, "caso": case,
            "utc": datetime.now(timezone.utc).isoformat(), "modo": run.mode, "modelo": run.model,
            "prompt_sha256": run.prompt_hash, "parametros": {"temperatura": 0, "max_saida": OUTPUT_ALLOWANCE},
            "limites": {"passos": MAX_STEPS, "tokens_entrada": INPUT_ALLOWANCE, "tokens_saida": OUTPUT_ALLOWANCE},
            "tokens": run.tokens, "trajetoria": run.events, "motivo_termino": reason,
            "latencia_total_ms": round((time.perf_counter() - started) * 1000),
            "saida": output,
        }
        self.logfile.parent.mkdir(parents=True, exist_ok=True)
        with self.logfile.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
        return output


def build_agent(db, logfile, *, mode="local", model=None):
    client = None
    model = model or os.getenv("LLM_MODELO") or MODEL
    if mode == "llm":
        from openai import OpenAI
        key = os.getenv("LLM_API_KEY") or os.getenv("GROQ_API_KEY")
        if not key:
            raise ValueError("Configure LLM_API_KEY (ou GROQ_API_KEY) para o modo llm")
        client = OpenAI(api_key=key, base_url=os.getenv("LLM_BASE_URL") or BASE_URL, timeout=20, max_retries=0)
    return Agent(Store(db, ROOT / "dados/veiculos.json", ROOT / "dados/estoque-demo.json"),
                 logfile, mode=mode, model=model, client=client)
