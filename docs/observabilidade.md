# Observabilidade | LuxCar Parte 3

## Plano

| Interessado | Pergunta | Decisão |
|---|---|---|
| Negócio | O agente chega a desfechos previstos? | Liberar só o fluxo demonstrado na suíte |
| Operação | Há atraso ou erro nas ferramentas? | Investigar componente e versão |
| Quem paga | Quanto custa uma execução? | Manter ou trocar modelo após medir consumo |
| Responsável | Dá para reconstruir uma ação sob determinada versão? | Reproduzir a decisão ou suspender o agente |

A raiz invoke_agent luxcar guarda entrada minimizada, versão, modelo configurado,
hashes dos prompts, ID de sessão, referências recuperadas, saída, fase e
término. A consulta remota tem filhos chat e execute_tool conforme as
operações. A retomada é outra raiz correlacionada pela sessão, com evento
de revisão e, se autorizada, execute_tool registrar_interesse.
[Convenções GenAI](https://opentelemetry.io/docs/specs/semconv/gen-ai/).

| Falha | Sinal |
|---|---|
| Erro de ferramenta | Status ERROR no span |
| Falha remota | Span chat com erro |
| Silenciosa: orçamento encerra sem erro | Motivo de término e SLI |
| Silenciosa: recibo sem efeito | Confronto do trace com SQLite na suíte |

## Medição e respostas

[Métricas](../evals/resultados/parte3-nova/metricas.json) e
[traces](../evals/resultados/parte3-nova/traces.jsonl). São 35 raízes da
versão 3.0.0 (30 entradas e cinco retomadas). A versão anterior não emitia
spans e não foi misturada.

- Negócio: 17 concluídas, sete sem fonte, quatro aguardando revisão, quatro
  com entrada insuficiente, duas fora de escopo e uma rejeitada.
- Operação: p50 de 5,666 ms e p95 de 9,090 ms. Erros de ferramenta: 0/19
  busca, 0/5 validação para revisão e 0/2 escrita.
- Quem paga: US$ 0,00 de API por execução local. A rodada Groq separada
  mediu US$ 0,003426 nos 27 spans com tokens. O custo total é desconhecido.
- Responsável: o [model card](model-card.md) reconstrói uma aprovação. A
  identidade no CLI é declarada, não autenticada.

## SLO

SLI: raízes com motivo completed, source_missing, out_of_scope,
insufficient_input, awaiting_human, human_rejected ou approval_expired,
divididas por todas as raízes da mesma versão e janela. Motivo vem do
atributo luxcar.motivo_termino. Erro, interrupção e orçamento esgotado não
contam como bons. O indicador mede desfecho, não substitui precisão.
SLO de bancada: ≥95% em sete dias. Janela observada: 35/35 (100%), consumo
de 0 de 1,75 falhas de orçamento teórico (0%). Se violar, isolar os motivos
e reexecutar a suíte após ajustar recuperação ou orçamento.


## Recorte remoto da versão 3.0.0

A [rodada Groq](../evals/resultados/parte3-groq-3.0.0/analise.md) tem
35 execuções, p50 de 1.130,051 ms e p95 de 1.896,122 ms. O negócio teve
25/30 casos aprovados, apesar de 35/35 términos previstos. Para operação,
3/30 chamadas remotas terminaram em erro, enquanto as ferramentas chamadas
não emitiram erro. Para quem paga, os 27 spans com tokens permitiram estimar
US$ 0,003426, sem estimar os três faltantes. Para o responsável, é possível
localizar a busca sem ano e a busca com marca incorreta no trace. A rodada
não exerceu a ferramenta do corpus. O SLO de término foi atingido neste
recorte, mas sozinho não demonstra qualidade remota.


## Recorte remoto da versão 3.0.1

A [rodada 3.0.1](../evals/resultados/parte3-groq-3.0.1/analise.md) tem
35 execuções, p50 de 1.036,327 ms e p95 de 2.095,094 ms. O negócio teve
28/30 casos aprovados. Para operação, 2/30 chamadas de modelo falharam,
sem erros nas ferramentas acionadas. Para quem paga, o custo parcial
estimado foi US$ 0,003502725, com uso conhecido em 28/30 spans. Para o
responsável, os dois traces de fallback identificam json_validate_failed.
O SLI de término foi 35/35, com 0% do orçamento consumido, mesmo com duas
falhas de integração. Os números das duas versões não foram agregados.
