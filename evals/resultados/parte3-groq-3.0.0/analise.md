# Rodada remota Groq | LuxCar 3.0.0

Rodada executada pelo grupo no Windows com GPT-OSS 20B e o dataset 2.0.0.
Resultado: **25/30 (83,3%)**. Em 27 casos a triagem veio do modelo. Em
três, o agente respondeu com a triagem local após erro da chamada. O
verificador corretamente não creditou fallback como êxito remoto.

| Caso | Evidência | Diagnóstico |
|---|---|---|
| p2-05 | Span chat ERROR, resposta local recusou consumo sem dado | Falha da chamada ou validação remota, sem código de erro registrado |
| 17 | Busca com ano nulo depois de pergunta com 2018 ou 2019 | Triagem não pediu esclarecimento e consultou sem filtrar o ano |
| 20 | Span chat ERROR, resposta local recusou quilometragem sem dado | Falha remota sem causa específica no trace |
| 26 | Busca enviou Civic como marca e modelo | Argumento errado levou a falso não encontrado |
| 29 | Span chat ERROR, resposta local recusou autonomia sem dado | Falha remota sem causa específica no trace |

Houve **35 execuções** (30 entradas e 5 retomadas), com p50 de **1.130,051 ms**
e p95 de **1.896,122 ms**. Foram 0/21 erros na busca de veículo, 0/5 na
validação para revisão e 0/2 na escrita. Houve 3/30 spans de modelo com erro.
O SLI de término previsto ficou em 35/35 (100%), acima da meta de 95%,
com 0% do orçamento consumido. Esse SLI não detectou as três quedas para
fallback nem os dois resultados funcionais incorretos. A cobertura remota
foi de 27/30 (90%). A comparação local/remota é de modo, não de versões.

O custo estimado dos **27 spans com uso informado** foi **US$ 0,003426**,
com 16.936 tokens de entrada e 7.186 de saída. A média desses 27 spans foi
US$ 0,00012689 por chamada. O custo total e por execução da rodada ficaram
indeterminados porque três tentativas não informaram uso. A rodada não
acionou a ferramenta do corpus documental.

O código 3.0.1 adiciona bloqueio para consulta com dois anos explícitos,
corrige marca repetida quando o catálogo aponta uma única marca para o
modelo e registra tipo/código do erro de fallback sem o corpo da resposta.
A regressão local passou em 30/30. Ainda não há uma rodada Groq em 3.0.1.

Fontes: [resumo](resumo.json), [casos](casos.jsonl), [traces](traces.jsonl)
e [métricas](metricas.json).
