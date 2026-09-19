# LuxCar — Fontes v1

Este documento reúne as fontes utilizadas na definição do case, da arquitetura, da análise de modelos e da base de conhecimento do LuxCar.

## 1. Fontes da disciplina

### Trabalho da disciplina — Parte 1

Enunciado da primeira entrega do trabalho de Agentes LLM.

Fonte:

https://github.com/celsocrivelaro/senac-agentes-llm/blob/main/trabalho/01-primeira-entrega.md

Consultado em setembro de 2026.

### Visão geral do trabalho

Documento utilizado para compreender a organização das três partes do projeto.

Fonte:

https://github.com/celsocrivelaro/senac-agentes-llm/blob/main/trabalho/00-visao-geral.md

Consultado em setembro de 2026.

---

## 2. Fontes técnicas

### Mistral AI — SDKs

Documentação oficial utilizada para consultar a utilização do SDK Python da Mistral.

Fonte:

https://docs.mistral.ai/resources/sdks

Consultado em setembro de 2026.

### Mistral AI — Primeiro API Request

Documentação oficial utilizada como referência para a integração do modelo com a aplicação Python.

Fonte:

https://docs.mistral.ai/getting-started/quickstarts/developer/first-api-request

Consultado em setembro de 2026.

### Mistral AI — Construção de agentes

Documentação oficial sobre utilização de agentes e chamadas de ferramentas.

Fonte:

https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent

Consultado em setembro de 2026.

### Mistral AI — Function Calling

Documentação oficial sobre utilização de ferramentas por meio de function calling.

Fonte:

https://docs.mistral.ai/studio/conversations/function-calling

Consultado em setembro de 2026.

### Mistral AI — Chat Completions

Documentação oficial sobre a API de conversação utilizada para interação com o modelo.

Fonte:

https://docs.mistral.ai/studio/conversations/chat-completion

Consultado em setembro de 2026.

### Mistral AI — API

Referência geral da API da Mistral.

Fonte:

https://docs.mistral.ai/api

Consultado em setembro de 2026.

---

## 3. Fontes utilizadas na análise de modelos

### OpenAI — Modelos

Documentação oficial utilizada como referência para o candidato GPT-5 mini na análise comparativa de modelos.

Fonte:

https://developers.openai.com/api/docs/models/gpt-5-mini

Consultado em setembro de 2026.

### Mistral AI — Preços

Página oficial utilizada como referência para análise de custos dos modelos da Mistral.

Fonte:

https://docs.mistral.ai/inference/pricing

Consultado em setembro de 2026.

### Google AI — Preços da Gemini API

Página oficial utilizada como referência para análise de custos dos modelos Gemini.

Fonte:

https://ai.google.dev/gemini-api/docs/pricing

Consultado em setembro de 2026.

---

## 4. Fonte de preços de veículos

### Fundação Instituto de Pesquisas Econômicas — FIPE

A FIPE é utilizada como referência para valores médios de veículos.

Fonte:

https://www.fipe.org.br/pt-br/indices/veiculos/

Consultado em setembro de 2026.

**Observação:** a FIPE informa que seus valores são referências médias para determinado período e que os preços efetivamente praticados podem variar.

A FIPE também informa em seu próprio site que não disponibiliza um serviço oficial de API. Portanto, uma futura integração de preços do LuxCar deverá utilizar uma fonte ou serviço de consulta compatível, sem afirmar que se trata de uma API oficial da FIPE.

---

## 5. Fontes de dados do LuxCar

### Base de veículos simulada

A primeira versão do LuxCar utiliza uma base de dados simulada localizada em:

```text
dados/veiculos.json