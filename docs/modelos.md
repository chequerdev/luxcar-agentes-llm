
---

# 2. `docs/modelos.md`

Aqui fiz uma mudança importante: **não vamos fingir que rodamos os 3 modelos**. O professor pede comparação e benchmark real; então o que ainda não foi executado fica claramente como pendente.

```markdown
# LuxCar — Análise de modelos v1

## 1. Objetivo

A análise de modelos tem como objetivo identificar quais características de um modelo de linguagem são relevantes para o funcionamento do LuxCar e definir critérios para comparar diferentes candidatos.

O LuxCar utiliza linguagem natural para interpretar perguntas sobre veículos e precisa ser capaz de utilizar ferramentas para consultar uma base estruturada.

Por isso, a análise concentra-se em características diretamente relacionadas ao caso.

---

## 2. Critérios de avaliação

Os critérios definidos para o LuxCar são:

| Critério | Por que é relevante para o LuxCar |
|---|---|
| Interpretação de linguagem natural | O usuário pode formular a mesma pergunta de diferentes maneiras |
| Function/tool calling | O modelo precisa solicitar consultas à base de veículos |
| Tratamento de informações incompletas | O usuário pode não informar ano, versão ou outro dado necessário |
| Tratamento de divergências | O usuário pode fornecer uma informação diferente daquela encontrada na base |
| Tratamento de registros inexistentes | O modelo não deve inventar informações quando não encontrar o veículo |
| Controle da resposta | A resposta deve ser objetiva e baseada nos dados recuperados |
| Latência | O sistema deve responder em tempo compatível com uma interação de chat |
| Consumo de tokens | O número de tokens influencia o custo de execução |
| Custo | O custo da API precisa ser compatível com o uso previsto |

O caso é predominantemente textual e, na primeira versão, não exige processamento de imagens ou áudio.

---

## 3. Modelos candidatos

Foram considerados três candidatos para comparação:

1. GPT-5 mini;
2. Mistral Small 4;
3. Gemini 3.1 Pro.

Além desses candidatos, a implementação atual do LuxCar utiliza o modelo:

```text
ministral-8b-2512