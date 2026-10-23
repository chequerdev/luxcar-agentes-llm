# Checklist de entrega — Parte 2

| Item | Estado | Evidência |
|---:|---|---|
| 0. complemento do case | concluído | `docs/case.md` |
| 1. entrada/saída | concluído | `src/contracts.py`, `docs/io.md`, testes |
| 2. prompts | concluído | `src/prompts/`, `docs/prompts.md`, log de ablação |
| 3. arquitetura | concluído | `docs/arquitetura.md` |
| 4. RAG | concluído | `src/retrieval.py`, `docs/rag.md`, corpus vigente/revogado |
| 5. memória | concluído com limitação declarada de remoção de logs/checkpoints | `src/memory.py`, `docs/memoria.md` |
| 6. grafo | concluído | `src/graph.py`, `conferir_grafo.py`, `docs/grafo.md` |
| 7. estado/reducers | concluído | `src/state.py`, log sem reducer |
| 8. human-in-the-loop | concluído | `interrupt`, SQLiteSaver, prazo, edição e idempotência |
| 9. casos | concluído | seis obrigatórios + um incompleto em `logs/parte2-caso-*.json` |
| 10. projeto | concluído | README, versões fixadas, `.env.example`, testes e comandos |

## Resultado validado em 23/10/2026

- `python -m pytest -q`: **14 passed** (Python 3.14 emite aviso conhecido do `langchain-core`; recomenda-se 3.12/3.13);
- `python evals/executar_suite.py --smoke --delay 0`: **1 aprovado**;
- `python conferir_grafo.py`: 15 nós incluindo início/fim e 20 arestas, 8 condicionais;
- seis casos obrigatórios: todos `execution_mode=llm`, provedor Groq, modelo `openai/gpt-oss-20b`;
- caso 6: `action_rows_after_two_approvals=1`;
- demonstração sem reducer: `InvalidUpdateError`, como registrado no log;
- busca por padrões de segredo: nenhum valor de chave encontrado.

## Comandos finais

```powershell
python -m pip install -r requirements.txt
$env:LUXCAR_USE_LLM='0'
python -m pytest -q
python evals/executar_suite.py --smoke --delay 0
python conferir_grafo.py
git diff --check
git status --short
git log -5 --oneline
git push origin main
```

O `push` não foi executado automaticamente; é o passo externo final do responsável pelo repositório.

