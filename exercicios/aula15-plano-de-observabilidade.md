# Exercício 15 — Plano de observabilidade do agente de trocas

**Sistema:** agente de trocas de loja virtual  
**Escopo:** aproximadamente 500 conversas/dia; modelo via API cobrado por tokens; limite de 6 passos por conversa.  
**Objetivo do plano:** verificar, sem ler o código, se o agente conclui corretamente os atendimentos, cumpre a política da loja e opera com custo e qualidade controlados.

## 1. As perguntas

| Interessado | Pergunta | Decisão que a resposta muda |
|---|---|---|
| Negócio (gestor da loja) | Qual percentual das solicitações de troca é resolvido pelo agente sem atendente humano? | Manter a operação automatizada ou revisar o fluxo quando ficar abaixo da meta de 60%. |
| Operação (equipe de atendimento) | Quantas conversas são encaminhadas por erro ou por esgotamento dos 6 passos? | Investigar integrações, revisar instruções e preparar capacidade de atendimento humano. |
| Quem paga (responsável financeiro) | Quantos tokens e quanto dinheiro são gastos por conversa concluída? | Ajustar o modelo, as instruções ou o orçamento quando o custo subir sem ganho de resolução. |
| Quem responde pelo sistema (responsável técnico) | Qual proporção das trocas registradas foi aprovada fora da política vigente? | Investigar decisões incorretas, suspender o registro automático se necessário e corrigir a versão do agente. |

## 2. O *trace* de uma conversa

Exemplo de execução típica em que o pedido está dentro do prazo, atende às condições e a troca é registrada. A resposta final ao cliente é enviada pela aplicação após a confirmação do registro.

```text
invoke_agent agente-de-trocas                 [raiz do trace]
├── chat modelo-via-api                      [identifica pedido e solicita consulta]
├── execute_tool consultar_pedido            [obtém data, produto, categoria e valor]
├── execute_tool consultar_politica          [obtém prazo e condições da categoria]
├── chat modelo-via-api                      [confere as regras e decide aprovar]
└── execute_tool registrar_troca             [registra a troca após a aprovação]
```

Nesse exemplo são **5 operações instrumentadas** abaixo da raiz, dentro do orçamento de **6 passos**. Em solicitações recusadas ou encaminhadas, não deve existir `execute_tool registrar_troca`.

**Atributos padronizados a registrar:**

- Raiz `invoke_agent agente-de-trocas`: `gen_ai.agent.name = agente-de-trocas` e `gen_ai.provider.name` (provedor utilizado).
- Em cada `chat <modelo>`: `gen_ai.request.model`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens` e `gen_ai.response.finish_reasons`.
- Em cada `execute_tool <ferramenta>`: `gen_ai.tool.name` e `gen_ai.tool.call.id`. Registrar também duração e status do *span*.

**Atributos específicos do domínio, gravados na raiz:**

| Atributo | Valores / significado | Para que serve |
|---|---|---|
| `troca.desfecho` | `aprovada`, `recusada`, `encaminhada`, `erro` | Calcular resolução automática e identificar encaminhamentos ou falhas. Considera-se resolvida automaticamente apenas uma aprovação registrada com sucesso ou uma recusa fundamentada, sem intervenção humana. |
| `troca.conformidade_politica` | `conforme`, `fora_politica`, `nao_aplicavel`, `nao_verificada` | Comparar cada aprovação registrada com as regras vigentes no momento da decisão, detectar aprovações indevidas e medir a taxa de violação. A verificação precisa ser independente da justificativa do próprio modelo. |
| `agente.passos_utilizados` | Inteiro de 1 a 6 | Detectar conversas que chegam ao limite e apoiar a investigação de laços e encaminhamentos. |

**Cuidados:** correlacionar os *spans* pelo identificador do *trace* e usar um identificador interno ou pseudonimizado do pedido, sem registrar dados pessoais ou o texto integral das mensagens por padrão. Somar tokens de entrada e saída dos *spans* `chat` para obter o consumo total por conversa, inclusive a estimativa de custo conforme o preço do modelo utilizado. As regras da política precisam ser versionadas para permitir auditoria posterior.

## 3. Os modos de falha

| Componente | Forma de falha | Tipo | Sinal observável |
|---|---|---|---|
| `consultar_pedido` | API do sistema de pedidos fica indisponível ou retorna erro. | **Ruidosa** | *Span* `execute_tool consultar_pedido` com status de erro, taxa de falhas e aumento de encaminhamentos por erro (`troca.desfecho = erro` ou `encaminhada`). |
| `consultar_politica` | Retorna prazo ou condições desatualizadas, sem informar erro. | **Silenciosa** | Aumento de `troca.conformidade_politica = fora_politica` nas aprovações, após checagem independente contra a versão vigente da política. |
| Modelo / decisão | Interpreta incorretamente o prazo ou uma exceção e aprova uma troca indevida. | **Silenciosa** | Proporção de aprovações registradas com `troca.conformidade_politica = fora_politica`; análise amostral das justificativas. |
| `registrar_troca` | A chamada falha e a troca aprovada não é efetivamente registrada. | **Ruidosa** | *Span* `execute_tool registrar_troca` com status de erro; aprovação sem confirmação de registro. |

Uma outra falha silenciosa importante a acompanhar é o agente encaminhar solicitações simples desnecessariamente: a conversa termina sem erro, mas a taxa de resolução automática cai.

## 4. Os objetivos (SLOs)

| SLO | Indicador | Objetivo | Janela |
|---|---|---|---|
| **SLO 1 — Operacional e eficiência** | Percentual de conversas que terminam com desfecho válido (`aprovada` registrada, `recusada` fundamentada ou `encaminhada` corretamente) **em até 6 passos e com até 3.000 tokens totais por conversa**. | **≥ 95%** das conversas. Os 3.000 tokens são uma meta operacional inicial, a recalibrar com dados reais e o preço do modelo. | **28 dias corridos**, janela móvel. |
| **SLO 2 — Promessa da loja** | **(a)** Taxa de resolução automática = conversas aprovadas e registradas ou recusadas corretamente, sem humano ÷ total de conversas elegíveis; **(b)** taxa de aprovação fora da política = trocas aprovadas e registradas em desacordo com a política ÷ total de trocas aprovadas e registradas. | **(a) ≥ 60%** de resolução automática **e (b) < 1%** de aprovações fora da política. As duas condições precisam ser cumpridas. | **28 dias corridos**, janela móvel. |

Para não inflar as métricas, contar cada conversa uma única vez, excluir apenas testes e duplicatas comprovadas, tratar resultados ainda não verificados como pendentes de auditoria e nunca considerar erro ou encaminhamento como resolução automática. A conformidade deve ser validada com referência independente à política vigente.

## 5. Os alertas

| Alerta | Condição e limiar | Quem é avisado | Ação esperada |
|---|---|---|---|
| **Custo / consumo de tokens** | Na última **1 hora**, mais de **5%** das conversas ultrapassam **3.000 tokens**, violando o componente de consumo do SLO 1 (margem equivalente à tolerância de 5% do SLO). Exigir amostra mínima de 20 conversas para reduzir ruído. | Responsável técnico e responsável financeiro. | Verificar tokens por modelo e por *trace*, número de chamadas, laços e mudanças recentes; comparar custo por conversa resolvida e otimizar instruções/modelo, sem cortar etapas de validação da política. |
| **Degradação silenciosa / decisão** | Nas últimas **24 horas**, taxa de resolução automática **< 60%** ou taxa auditada de aprovações fora da política **≥ 1%** (limiares do SLO 2). Com baixa quantidade de aprovações auditadas, qualquer violação confirmada gera revisão humana imediata. | Responsável técnico, operação e gestor da loja. | Conferir versão da política e decisões recentes, revisar os *traces* e os casos afetados, corrigir regras/prompt; se houver aprovações indevidas confirmadas, interromper temporariamente `registrar_troca` no modo automático e encaminhar casos a humanos até corrigir a causa. |

Os alertas usam janelas curtas para detectar deterioração antes do fechamento do SLO de 28 dias. As taxas finais são sempre apuradas pela janela oficial dos SLOs; os alertas são gatilhos antecipados de investigação.

## Resposta à questão final

É possível saber se o agente está funcionando sem ler o código observando os *traces* de cada conversa, os resultados das ferramentas, os desfechos registrados, a quantidade de passos e o consumo de tokens. Ele **funciona** quando consegue consultar pedido e política, produzir um desfecho e registrar uma troca somente quando apropriado. Ele **funciona bem** quando, além de não apresentar erros relevantes, conclui ao menos 95% das conversas dentro do orçamento operacional, resolve ao menos 60% dos casos elegíveis sem humanos e mantém menos de 1% das aprovações registradas fora da política. Os alertas permitem agir quando custo ou qualidade começam a piorar, inclusive nos casos em que o agente responde normalmente, mas toma decisões erradas.