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
- Quem paga: US$ 0,00 de API por execução local. **LACUNA:** custo remoto
  não medido, pois não houve chamadas remotas na rodada.
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
