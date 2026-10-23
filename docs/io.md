# Entrada e saída

## Contratos

`AgentInput` (`src/contracts.py`) aceita texto livre e metadados não digitados: `user_id`, `session_id` e `case_id`. O `thread_id` é `user_id:session_id:case_id`.

`AgentOutput` proíbe campos extras e exige:

- `result`: resposta ou recusa;
- `sources`: lista verificável de `SourceEvidence`, inclusive quando vazia;
- `sufficient`: base suficiente ou não;
- `status` e `termination_reason` enumerados;
- contadores de recuperação e ferramentas;
- `thread_id` e, quando aplicável, a ação.

## Exemplos copiados de execução

Data: **23/10/2026**. Código executado: commit **`890dc8a9da981e0a8e8de90325277903f296aa6c`**, com `worktree_dirty: false` no início. Os hashes dos prompts e da árvore `src/` estão nos logs.

### Caminho feliz

Entrada exata:

```text
Qual câmbio o Polo TSI 2018 possui?
```

Saída completa:

```json
{
  "result": "Segundo o cadastro, o Volkswagen Polo TSI 2018 tem câmbio: Automático de 6 velocidades.",
  "sources": [{"source_id":"veiculo:1","source_type":"structured_record","location":"dados/veiculos.json#id=1","excerpt":"Volkswagen Polo TSI 2018: motor=1.0 TSI, potencia_cv=128, torque_kgfm=20.4, combustivel=Flex, cambio=Automático de 6 velocidades","score":1.0,"current":true}],
  "sufficient": true,
  "status": "answered",
  "termination_reason": "completed",
  "retrieval_calls": 1,
  "tool_calls": ["buscar_veiculo"],
  "thread_id": "demonstracao:2026-10-23T03:45:04.886302+00:00:01-simples",
  "action": null
}
```

O que ler: a resposta é sustentada por `veiculo:1`, tem suficiência positiva e exatamente uma recuperação. Log: `logs/parte2-caso-01-simples.json`.

### Recusa por fonte ausente

Entrada exata:

```text
Qual é o consumo rodoviário do Polo TSI 2018?
```

Saída completa:

```json
{
  "result": "A base não possui o atributo pedido ou a pergunta não especifica qual dado técnico consultar.",
  "sources": [{"source_id":"veiculo:1","source_type":"structured_record","location":"dados/veiculos.json#id=1","excerpt":"Volkswagen Polo TSI 2018: motor=1.0 TSI, potencia_cv=128, torque_kgfm=20.4, combustivel=Flex, cambio=Automático de 6 velocidades","score":1.0,"current":true}],
  "sufficient": false,
  "status": "not_found",
  "termination_reason": "source_missing",
  "retrieval_calls": 1,
  "tool_calls": ["buscar_veiculo"],
  "thread_id": "demonstracao:2026-10-23T03:45:04.886302+00:00:05-fora-do-corpus",
  "action": null
}
```

O que ler: o registro existe, mas não contém consumo; `sufficient: false` impede transformar combustível em consumo. Esse portão foi adicionado após uma execução real detectar justamente esse falso positivo. Log: `logs/parte2-caso-05-fora-do-corpus.json`.

### Entrada incompleta

Entrada exata:

```text
Qual câmbio ele usa?
```

Saída completa:

```json
{
  "result": "Preciso de marca, modelo, ano, versao para responder sem adivinhar.",
  "sources": [],
  "sufficient": false,
  "status": "clarification_needed",
  "termination_reason": "insufficient_input",
  "retrieval_calls": 0,
  "tool_calls": [],
  "thread_id": "demonstracao:2026-10-23T03:45:04.886302+00:00:07-entrada-incompleta",
  "action": null
}
```

O que ler: nenhum dado foi inventado e nenhuma busca inútil ocorreu. Log: `logs/parte2-caso-07-entrada-incompleta.json`.

## Ambiguidade e fora do escopo

- dois anos na mesma pergunta são encaminhados para esclarecimento pela regra em código;
- pergunta não automotiva termina em `out_of_scope` sem recuperação;
- modelo/ano inexistente termina em `source_missing`, sem gerar registro fictício.

