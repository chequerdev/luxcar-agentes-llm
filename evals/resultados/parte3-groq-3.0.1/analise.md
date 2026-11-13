# Rodada Groq | LuxCar 3.0.1

A mesma suíte, com o dataset 2.0.0 e GPT-OSS 20B na Groq, passou de
25/30 na [versão 3.0.0](../parte3-groq-3.0.0/analise.md) para **28/30
(93,3%)**, ganho de 10 pontos percentuais. A nova rodada foi executada pelo
grupo no Windows no commit 1c04025.

| Caso | 3.0.0 | 3.0.1 |
|---|---|---|
| 17 | Buscou sem ano | Pediu um único ano, sem buscar |
| 26 | Enviou Civic como marca | Retornou 173 cv para o Honda Civic Touring 2020 |
| 20 | Fallback local | Triagem remota e recusa esperada |
| p2-05 e 29 | Fallback local | Groq rejeitou a geração JSON com json_validate_failed. O fallback local devolveu o estado esperado, mas a suíte não o creditou como aprovação remota. |

Foram 35 execuções, com p50 de **1.036,327 ms** e p95 de **2.095,094 ms**.
A latência p50 caiu e a p95 subiu em relação à 3.0.0. Houve dois erros em
30 spans de modelo e zero erros nas ferramentas acionadas (0/20 na busca,
0/5 na validação e 0/2 no registro). O SLI de término marcou 35/35,
acima do SLO de 95%, com 0% do orçamento consumido. As duas falhas de
integração ficaram invisíveis para esse SLI isolado, mas apareceram nos
spans de modelo e na suíte.

Os 28 spans com uso registrado somaram 17.563 tokens de entrada e 7.285
de saída. Pelas tarifas documentadas no repositório, o custo parcial
estimado foi **US$ 0,003502725**, aproximadamente US$ 0,00012510 por chamada
com consumo registrado. As duas chamadas sem uso informado impedem estimar
o custo total e a média por execução completa. A rodada não acionou a
ferramenta do corpus documental.

Evidências: [resumo](resumo.json), [casos](casos.jsonl),
[traces](traces.jsonl) e [métricas](metricas.json).
