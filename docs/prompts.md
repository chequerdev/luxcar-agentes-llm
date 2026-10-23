# Plano de prompt engineering

Os prompts executáveis ficam em `src/prompts/`; este documento registra decisões. Cada execução grava o SHA-256 abreviado de cada arquivo.

| Etapa | Técnica e razão | Contrato exato | Teste |
|---|---|---|---|
| Triagem | zero-shot com enumeração de rotas; a intenção depende de julgamento sobre texto livre | JSON de `TriageDecision`; `route` é `Literal`; campos extras são proibidos; sem markdown | sete casos reais + suíte; Pydantic rejeita formato inválido |
| Resposta | grounding/decomposição: recuperar antes, sintetizar depois; nesta versão a síntese final é determinística | `AgentOutput`; é proibido responder atributo ausente ou fonte revogada | casos 1, 2, 3 e 5; contrato e fontes conferidos |
| Extração de memória | instrução restritiva; só fatos duráveis explicitamente permitidos | lista JSON `{key,value}`; sem dados sensíveis/inferidos | testes unitários da política; chamada LLM reservada à evolução |
| Aprovação humana | prompt informativo no `interrupt` | ação, argumentos, consequência, respostas `approve/reject/edit`, prazo | caso 6 com edição e repetição |

## Versões efetivas em 23/10/2026

- `triage-v2.md`: `73dd0062a80a`
- `answer-v2.md`: `53be67ccec2c`
- `memory-extraction-v2.md`: `e104193d05c9`

## Regra da frase: ablação real

Frase retirada experimentalmente: **“Nunca complete ano, versão, telefone ou veículo por suposição.”**

Três entradas incompletas foram chamadas com e sem a frase no Groq/modelo `openai/gpt-oss-20b`. Em todos os três pares, o modelo manteve os campos ausentes como `null`; mudaram apenas justificativa/confiança. Evidência: `logs/parte2-ablation-prompt.json`.

A frase **voltou** e permanece no prompt. Três casos são uma amostra pequena para remover uma barreira contra escrita com telefone/veículo inventado; o custo é baixo e o risco da rota `register_interest` é alto. Uma ablação maior pode justificar remoção futura.

## Fallback

Falha, ausência de chave ou JSON inválido ativa um classificador conservador e registra `mode: deterministic_fallback` e o motivo. Os logs entregues registram `mode: llm`; não há substituição silenciosa.

