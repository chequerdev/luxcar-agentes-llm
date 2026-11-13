# LuxCar | Trabalho 3 — O sistema sob controle

Entrega da disciplina de Agentes de IA do Senac, por Gabriel Chequer de
Oliveira e Anderson Clayton Ferreira Junior. A Parte 3 usa o grafo da
Parte 2 em `src.main`: consulta catálogo e documentos, e só registra
interesse após revisão humana. O protótipo comercial de negociação está
preservado mais abaixo e não é a entrada desta avaliação.

## Reprodução no Windows (PowerShell)

Use Python 3.12 e rode na raiz do repositório. Não é necessário ativar a
venv nem configurar uma chave para reproduzir a suíte local.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:LUXCAR_USE_LLM = "0"
.\.venv\Scripts\python.exe -m src.main "Qual câmbio o Polo TSI 2018 possui?"
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m evals.rodar --modo local --saida ".runtime/rodada-$(Get-Date -Format yyyyMMdd-HHmmss)"
```

No Linux/macOS, crie o ambiente com `python3.12 -m venv .venv`, ative
com `source .venv/bin/activate`, use `python` nos comandos e exporte
`LUXCAR_USE_LLM=0`. Para a suíte, indique um diretório de saída novo.

Uma [execução local registrada](evals/resultados/parte3-nova/casos.jsonl)
respondeu “Segundo o cadastro, o Volkswagen Polo TSI 2018 tem câmbio:
Automático de 6 velocidades.” A fonte foi `veiculo:1`, com status
`answered` e término `completed`.

## Comparações e traces

```bash
python -m evals.comparar evals/resultados/parte3-anterior evals/resultados/parte3-nova
python -m evals.comparar evals/resultados/parte3-groq-3.0.0 evals/resultados/parte3-groq-3.0.1
python -m evals.metricas evals/resultados/parte3-groq-3.0.1/traces.jsonl
```

No Windows, use `.\.venv\Scripts\python.exe` no lugar de `python`
se a venv não estiver ativada. Cada rodada grava `resumo.json`,
`casos.jsonl` e `traces.jsonl` na pasta de saída. Para uma consulta
avulsa com trace, defina `LUXCAR_TRACE_FILE=.runtime/trace.jsonl` no
ambiente. A [demo de recuperação documental](evals/resultados/parte3-corpus-local-3.0.1/analise.md)
traz exemplo, saída e trace.

Resultados versionados: **26/30 → 30/30 no modo local**, **25/30 → 28/30
na Groq** e **22/30 acordos com o juiz LLM**, que não foi adotado. Para
repetir o modo remoto, copie `.env.example` para `.env`, configure
`GROQ_API_KEY` e rode `python -m evals.rodar --modo llm --intervalo 15 --saida .runtime/rodada-remota`
com uma pasta nova. Use apenas dados fictícios e não inclua a chave no Git.

Veja [guia da entrega](docs/entrega-parte3.md),
[avaliação](docs/evals.md), [model card](docs/model-card.md),
[segurança](docs/seguranca.md), [observabilidade](docs/observabilidade.md),
[mudanças](docs/mudancas.md) e [roteiro da apresentação](docs/apresentacao.md).

## Referência da Parte 1 — protótipo comercial

O fluxo comercial decide se uma proposta pode ser aberta para um veículo. Ele
bloqueia unidade indisponível, negociação ativa ou valor abaixo do mínimo. Uma
proposta só é gravada no SQLite depois da confirmação explícita do vendedor.
O fluxo anterior de consulta técnica e RAG continua disponível abaixo.

### Demonstrar negociação

Modo local (sem chave), a partir da raiz do repositório:

```bash
python -m src.negociacao --modo local --vendedor demo --mensagem 'Abra uma proposta para o Polo por R$ 70.000,00'
python -m src.negociacao --vendedor demo --confirmar ID_DA_REVISAO
python -m src.negociacao --modo local --vendedor outro --mensagem 'O Polo está disponível?'
```

Substitua `ID_DA_REVISAO` pelo valor da primeira saída. No segundo comando use
`--rejeitar` no lugar de `--confirmar` para testar a recusa. Para repetir desde
o zero sem alterar a primeira demonstração, use `--db` com um novo arquivo
SQLite em todos os comandos.

No modo LLM instale `requirements.txt`, copie `.env.example` para `.env` e
configure `LLM_API_KEY` (ou `GROQ_API_KEY`). Para Groq, o padrão é
`LLM_BASE_URL=https://api.groq.com/openai/v1` e
`LLM_MODELO=openai/gpt-oss-20b`. Troque `--modo local` por `--modo llm` na
mensagem. Não coloque a chave no Git.

```bash
python -m pytest -q
python -m scripts.avaliar_negociacao --saida .runtime/eval-negociacao
python -m scripts.avaliar_negociacao --modo comparar --saida .runtime/comparacao
python -m scripts.medir_fluxo_manual --operador vendedor_demo
```

A comparação de modelos exige chave e executa 15 chamadas. Os logs do modo local
disponíveis em `logs/negociacao/local/` não comprovam chamadas a modelo.
Veja [caso](docs/case.md), [arquitetura](docs/arquitetura-v1.md),
[comparação](docs/modelos.md) e [rastreabilidade da devolutiva](docs/correcoes-parte1.md).

## Referência histórica da Parte 2 — consulta e RAG

O LuxCar recebe uma pergunta em texto livre, identifica a intenção com LLM, consulta registros ou documentos e devolve um objeto Pydantic com resultado, fontes e suficiência. Uma solicitação de interesse só é gravada depois de revisão humana.

### Rodar em menos de cinco minutos

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
tests/                 testes automatizados
```

## Limites honestos

- corpus e veículos são simulados; não há preço ou estoque em tempo real;
- o checkpoint e a memória ficam em SQLite local, sem replicação;
- a busca documental é textual, não vetorial;
- o modelo só classifica/extrai a intenção; código controla suficiência e escrita;
- logs podem conter argumentos de demonstração e devem ser tratados conforme a política de retenção.

Detalhes: `docs/io.md`, `docs/prompts.md`, `docs/arquitetura.md`, `docs/rag.md`, `docs/memoria.md`, `docs/grafo.md` e `docs/humano.md`.
