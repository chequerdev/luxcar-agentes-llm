# Grafo, padrões e lacunas do framework

## Padrões usados

| Padrão | Onde | Por que este nível | Condição de não uso |
|---|---|---|---|
| sequencial com portão | inicialização → memória → triagem; aprovação → escrita | pré-condições verificáveis | não usar modelo para campo vazio/prazo |
| router | saída de `triage` | intenção em texto livre exige julgamento | fallback explícito quando LLM indisponível |
| agente (laço) | **não usado** | rotas e ferramentas são finitas | só adotar se consultas multi-etapas reais exigirem repetição |
| paralelização | **não usada** | corpus pequeno e uma fonte por rota | adotar apenas com medição de latência |
| orquestrador-trabalhador | **não usado** | não há decomposição dinâmica | — |
| avaliador-otimizador | **não usado** | contrato/portões bastam nesta versão | — |

## Quem decide cada bifurcação

- `triage`: modelo, com saída `Literal` validada; fallback por regras é registrado;
- rota de escrita explícita e atributos fora do schema: regra em código;
- resultado encontrado/suficiente: regra sobre registros/fontes;
- humano aprovado/rejeitado/expirado: objeto Pydantic + timestamp;
- repetição de escrita: chave SHA-256 e unicidade SQLite.

## Conferência contra o código

Comando: `python conferir_grafo.py`.

```text
NÓS
__start__, initialize, recall_memory, triage, clarify, refuse,
lookup_vehicle, retrieve_documents, synthesize, prepare_action,
human_approval, write_action, rejected, expired, __end__

ARESTAS CONDICIONAIS
triage -> clarify | lookup_vehicle | prepare_action | refuse | retrieve_documents
human_approval -> expired | rejected | write_action
```

As demais arestas são as sequenciais desenhadas em `docs/arquitetura.md`.

## O que o framework não deu

- taxonomia de término: implementada em `AgentOutput.termination_reason` e nos nós terminais;
- detector de laço: não foi necessário porque este grafo é acíclico; `recursion_limit=20` limita dano, mas não seria detector;
- teto de tempo: timeout de 15 s no cliente; o LangGraph não impõe o orçamento total de 30 s;
- erro recuperável/fatal: falha de triagem LLM é recuperável e aciona fallback; contrato/checkpoint inválido é fatal;
- idempotência de escrita: implementada em `MemoryStore.record_action`.

## Decisão que virou parâmetro

`recursion_limit` é passado explicitamente como 20; depender do default faria uma atualização alterar custo máximo sem revisão. `RAG_TOP_K=3` e timeout de 15 s também são explícitos. O grafo é compilado uma vez no import de `src.graph`.

