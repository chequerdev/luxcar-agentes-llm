# Rastreabilidade | devolutiva da Parte 1

| Rubrica | Onde conferir |
|---|---|
| 1a, 1b, 1e | `docs/case.md`, seções 1 e 5; tempo manual em loja não disponível e cronometragem acadêmica pendente; `scripts/medir_fluxo_manual.py` pronto |
| 1c, 1d | `docs/case.md` seção 4, `evals/negociacao-casos.json`, `scripts/avaliar_negociacao.py` |
| 2a–2d | `docs/case.md` seção 2 |
| 3a–3c | Sete passos em `docs/case.md` seção 3 |
| 5a–5d | `docs/modelos.md`; projeção e critério de troca registrados; comparação empírica de 15 chamadas pendente |
| 6a | `src/negociacao/agent.py`, `requirements.txt`, `.env.example` |
| 6b, 6c | Estado e trajetória em `src/negociacao/agent.py`, camada SQLite/JSON em `src/negociacao/store.py` |
| 6d | `logs/negociacao/local/`, com geração pelo programa e modo local declarado; contrato do SDK testado com transporte simulado em `tests/test_negociacao.py`; faltam logs da API real |
| 8a, 8b | `docs/arquitetura-v1.md` |
| 9a, 9b | `prompts/luxcar-v1.md`, comentário na chamada e carimbo SHA-256 nos logs |
| Arquivos cortados e preâmbulos | `docs/case.md`, `docs/modelos.md`, `docs/base-de-conhecimento-v1.md` reescritos |

Os arquivos `logs/caso-0*.json` e `logs/historico.jsonl` preexistentes são históricos da Parte 1, não evidência do fluxo comercial. O agente de consulta/RAG anterior permanece reproduzível em `src.main` e os respectivos logs da Parte 2 não foram sobrescritos.
