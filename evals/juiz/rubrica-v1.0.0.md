# Rubrica v1.0.0 | utilidade do próximo passo

Propriedade única: quando o agente não resolve o pedido imediatamente, a
resposta deixa claro o próximo passo permitido ou por que não há próximo passo
neste canal? Considere só a pergunta e o texto entregue. Não avalie precisão
da ficha técnica. Responda JSON {"util": true ou false, "nota": "uma frase"}.
Para uma resposta final que resolve diretamente a pergunta, marque true
se ela fornece uma resposta direta sem instrução contraditória.

Positivo: “Informe modelo e ano para eu identificar a ficha.” A pessoa sabe
quais dados fornecer.

Negativo: “Operação não concluída.” A pessoa não sabe se deve corrigir,
aguardar, repetir ou procurar outro canal.

Limiar pré-definido: adotar somente com pelo menos 90% de concordância em no
mínimo 20 rótulos humanos independentes, com exemplos das duas classes, e
zero falsos positivos em saída que sugira escrita já concluída sem confirmação.
Não alterar o limiar depois de ver os resultados.
