# LuxCar — agente de consulta automotiva

O LuxCar recebe uma pergunta em texto livre, identifica a intenção com LLM, consulta registros ou documentos e devolve um objeto Pydantic com resultado, fontes e suficiência. Uma solicitação de interesse só é gravada depois de revisão humana.

## Rodar em menos de cinco minutos

Recomendado: Python 3.12 ou 3.13. A suíte também passa no Python 3.14, com um aviso de compatibilidade emitido pelo `langchain-core`.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Preencha uma chave em `.env` (`GROQ_API_KEY`, `XAI_API_KEY` ou `OPENAI_API_KEY`) e, quando necessário, `LUXCAR_MODEL` e `LUXCAR_BASE_URL`. Sem chave, o sistema usa e registra um classificador determinístico conservador; ele nunca finge que chamou um modelo.

```powershell
python -m src.main "Qual câmbio o Polo TSI 2018 possui?" --user-id demo --session-id conversa-1
```

Saída real de 23/10/2026, código no commit `890dc8a9da981e0a8e8de90325277903f296aa6c`:

```json
{
  "result": "Segundo o cadastro, o Volkswagen Polo TSI 2018 tem câmbio: Automático de 6 velocidades.",
  "sources": [{
    "source_id": "veiculo:1",
    "source_type": "structured_record",
    "location": "dados/veiculos.json#id=1",
    "excerpt": "Volkswagen Polo TSI 2018: motor=1.0 TSI, potencia_cv=128, torque_kgfm=20.4, combustivel=Flex, cambio=Automático de 6 velocidades",
    "score": 1.0,
    "current": true
  }],
  "sufficient": true,
  "status": "answered",
  "termination_reason": "completed",
  "retrieval_calls": 1,
  "tool_calls": ["buscar_veiculo"],
  "thread_id": "demonstracao:2026-10-23T03:45:04.886302+00:00:01-simples",
  "action": null
}
```

O objeto completo está em `logs/parte2-caso-01-simples.json`.

## Quando o grafo para

O pedido abaixo não grava nada imediatamente:

```powershell
python -m src.main "Registre meu interesse no Polo TSI 2018, telefone 11999998888" --user-id demo --session-id conversa-2 --case-id proposta
```

A saída terá `status: "pending_approval"` e um `thread_id`. Um operador pode rejeitar, aprovar ou editar:

```powershell
python -m src.main --resume-thread "demo:conversa-2:proposta" --decision edit --edits '{"contact":"11888887777"}'
```

Após 24 horas, uma retomada expira sem gravar. A chave de idempotência deriva do conteúdo: aprovação repetida não duplica a solicitação.

## Verificação e entrega

```powershell
$env:LUXCAR_USE_LLM='0'
python -m pytest -q
python conferir_grafo.py
python -m scripts.demonstrar_reducer
python -m scripts.gerar_logs_parte2
git status --short
git log -5 --oneline
```

`scripts/gerar_logs_parte2.py` usa o provedor configurado. Confira `metadata.execution_mode` em cada log; `llm` só aparece quando a chamada foi bem-sucedida.

## Estrutura principal

```text
src/contracts.py       entrada, saída e decisão Pydantic
src/graph.py           StateGraph compilado e human-in-the-loop
src/retrieval.py       consulta estruturada e busca textual
src/memory.py          memórias e escrita idempotente em SQLite
src/prompts/           prompts carregados em execução
dados/corpus/          documentos vigentes e revogado
docs/                  decisões e evidências de projeto
logs/parte2-*.json     execuções reais da Parte 2
tests/                 13 testes automatizados
```

## Limites honestos

- corpus e veículos são simulados; não há preço ou estoque em tempo real;
- o checkpoint e a memória ficam em SQLite local, sem replicação;
- a busca documental é textual, não vetorial;
- o modelo só classifica/extrai a intenção; código controla suficiência e escrita;
- logs podem conter argumentos de demonstração e devem ser tratados conforme a política de retenção.

Detalhes: `docs/io.md`, `docs/prompts.md`, `docs/arquitetura.md`, `docs/rag.md`, `docs/memoria.md`, `docs/grafo.md` e `docs/humano.md`.
