# Análise de modelos | LuxCar comercial

A comparação usa a mesma configuração de Chat Completions compatível com OpenAI para os três candidatos. O critério principal é o acerto da rota e dos argumentos, porque a ação errada pode gerar uma revisão para outro veículo. A taxa de seleção que respeita o contrato mede se a resposta pode ser executada. A latência afeta o atendimento enquanto o vendedor está com o cliente. O custo importa para projeção mensal ou semestral. O verificador avalia a decisão inteira, inclusive a ausência de proposta sem confirmação.

| Candidato Groq | Suporte a ferramentas | Entrada/saída USD por milhão | Hipótese a testar |
|---|---|---:|---|
| `openai/gpt-oss-20b` | Sim | 0,075 / 0,30 | Custo menor mantendo 5/5 casos |
| `openai/gpt-oss-120b` | Sim | 0,15 / 0,60 | Pode reduzir erros de interpretação em pedidos ambíguos |
| `qwen/qwen3.8-27b` | Sim, em preview | 0,80 / 4,00 | Candidato multilíngue para testar referências e valores em português |

Fontes de capacidade e tarifa: [GPT-OSS 20B](https://console.groq.com/docs/model/openai/gpt-oss-20b), [GPT-OSS 120B](https://console.groq.com/docs/model/openai/gpt-oss-120b) e [Qwen 3.8 27B](https://console.groq.com/docs/model/qwen/qwen3.8-27b). Verifique tarifas antes de reproduzir a conta.

## Projeção de custo

Para cada chamada, some `(tokens de entrada × tarifa de entrada + tokens de saída × tarifa de saída) / 1.000.000`. Some todas as chamadas da execução. O pedido faz uma chamada e a confirmação não usa o modelo. A média observada deve ser multiplicada por 100 ou pelo volume semestral estimado. Cenário ilustrativo: 1.000 tokens de entrada e 150 de saída por pedido, sem cache, com 2.000 pedidos por semestre. Não são valores medidos.

| Modelo | USD/pedido | USD/100 pedidos | USD/semestre |
|---|---:|---:|---:|
| GPT-OSS 20B | 0,000120 | 0,0120 | 0,240 |
| GPT-OSS 120B | 0,000240 | 0,0240 | 0,480 |
| Qwen 3.8 27B | 0,001400 | 0,1400 | 2,800 |

## Protocolo e decisão

Execute `python -m scripts.avaliar_negociacao --modo comparar --saida logs/negociacao/comparacao` com `LLM_API_KEY` ou `GROQ_API_KEY`. O script roda os mesmos cinco casos com cada um dos três modelos. Ele usa a ferramenta, argumentos, motivo final, estado do banco, tokens e latência registrados pelo agente. Não converte falhas da API em resultado local. Confirmação humana no experimento é uma chamada de teste explícita definida pelo rótulo.

**Status:** os cinco casos locais foram executados. As quinze chamadas reais da nova suíte dependem de uma chave Groq e não estão comprovadas nesta versão. Resultados do agente anterior ou simulações não contam para esta comparação. O modelo padrão provisório é GPT-OSS 20B por custo e suporte ao contrato. Trocar se ficar abaixo de 5/5 e um concorrente atingir 5/5 sem escrita antecipada. Se os três passarem, manter o menor custo observado, desde que a latência mediana fique em até 3 segundos. Se nenhum passar, corrigir extração e prompt e reexecutar antes de declarar uma escolha validada.
