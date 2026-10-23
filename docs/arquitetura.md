# Arquitetura da Parte 2

## Diagrama executável

```text
texto livre + user/session/case
             |
             v
 [initialize: código] -> [recall_memory: código/SQLite]
             |
             v
 [triage: MODELO; fallback explícito]
    | regra/rota validada por Pydantic
    +--> clarify -------------------------------> END insuficiente
    +--> refuse --------------------------------> END fora do escopo
    +--> lookup_vehicle [consulta estruturada] --+
    |                                            v
    +--> retrieve_documents [busca textual] --> synthesize [código] -> END
    |
    +--> prepare_action [código]
              |
              v
       human_approval [INTERRUPT / operador LuxCar]
          | aprovar/editar       | rejeitar       | >24 h ao retomar
          v                      v                v
       write_action          rejected          expired
       [SQLite/idempotente]      \                /
          |                       +------ END ----+
          v
         END

Dados: dados/veiculos.json | dados/corpus/*.json
Memória/checkpoint: .runtime/memory.sqlite | .runtime/checkpoints.sqlite
```

Cada nó acima existe em `src/graph.py`; o script `conferir_grafo.py` importa o mesmo objeto `graph` compilado.

## As seis decisões

| Pergunta | Resposta atual |
|---|---|
| Ferramentas | `buscar_veiculo` e `buscar_corpus_textual` são leituras reversíveis; `registrar_interesse` é escrita persistente e idempotente. |
| Laço | Não há laço livre. A topologia é um roteador com portões; autonomia adicional não resolveria um problema observado. |
| Estado | Identidade, decisão, fontes, contadores, eventos e ação são campos explícitos. Texto conversacional fica em `input.text`; resultados derivados não são duplicados. |
| Orçamento | `recursion_limit=20` é explícito; DAG tem no máximo 7 nós; chamada externa tem timeout de 15 s; orçamento de projeto é 30 s. |
| Término | `completed`, `insufficient_input`, `out_of_scope`, `source_missing`, `awaiting_human`, `human_rejected`, `approval_expired`, limites e erros recuperável/fatal. |
| Humano | Operador LuxCar revisa somente escrita de interesse. Vê ação, argumentos e consequência; pode aprovar, rejeitar ou editar; após 24 h a retomada expira. |

## Autonomia mínima

Nível: **roteador com decisão LLM**, não agente em laço. Um workflow puramente por regras não cobre bem todas as formulações livres de intenção/entidade; por isso o modelo decide `route` e extrai campos. O degrau acima (agente que escolhe ferramentas repetidamente) não é necessário: consulta e escrita possíveis são poucas, estáveis e verificáveis.

Decisões de segurança continuam no código: uma escrita exige a palavra “interesse”; atributos inexistentes no schema, como consumo/preço, são bloqueados mesmo que o modelo os confunda; fontes revogadas não sustentam resposta.

## Ferramentas

| Ferramenta | Efeito | Reversível | Proteção |
|---|---|---|---|
| `buscar_veiculo` | lê JSON estruturado | sim | igualdade normalizada |
| `buscar_corpus_textual` | lê e ranqueia seções | sim | status vigente + `k=3` |
| `registrar_interesse` | grava linha SQLite | remoção administrativa | `interrupt`, edição humana e SHA-256 do conteúdo |

## Estado

| Campo | Tipo/reducer | Escreve | Lê | Origem |
|---|---|---|---|---|
| `input` | dict, substituição | API | triagem e nós | `AgentInput` |
| `thread_id` | str | API | saída/checkpoint | identidade |
| `started_at`, `steps` | float/int | nós | diagnóstico | execução |
| `decision` | dict | triagem | roteador/consulta | `TriageDecision` |
| `sources` | lista, `operator.add` | recuperadores | síntese | ferramentas |
| `tool_calls` | lista, `operator.add` | ferramentas | saída/log | execução |
| `events` | lista, `operator.add` | todos os nós | logs | observabilidade |
| `retrieval_calls` | int, `operator.add` | recuperadores | saída | medição RAG |
| `recalled_memories` | lista, `operator.add` | memória | evolução futura | SQLite |
| `proposed_action` | dict | preparo/humano | aprovação/escrita | texto + edição |
| `action_result` | dict | humano/escrita | roteador/saída | HITL |
| `output` | dict | terminais | API | `AgentOutput` |

Sem reducer, dois ramos que escrevem `evidence` na mesma superetapa produzem `InvalidUpdateError` no LangGraph 1.0.7 (a versão atual não sobrescreve silenciosamente). Execução real: `logs/parte2-reducer-sem-reducer.json`.

Não ficam no estado: cliente de API, conexões SQLite, corpus carregável, prompt e schema (recursos do processo). Também não se guarda `sufficient` separadamente antes da saída, pois é derivado das fontes e da decisão.

