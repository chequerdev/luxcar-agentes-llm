# Validação do juiz | rubrica 1.0.0

Foram avaliadas 30 saídas com GPT-OSS 20B via Groq, comparadas com os
[rótulos humanos](rotulos-humanos.csv). O [JSON bruto](resultado-bruto.json)
foi preservado. O limiar de 90% foi definido antes da medição na
[rubrica](../../juiz/rubrica-v1.0.0.md).

| Humano ↓ / Juiz → | 0 | 1 |
|---|---:|---:|
| 0 | 1 | 1 |
| 1 | 7 | 21 |

**22/30 acordos (73,3%). Juiz não adotado.** O limiar exigia ao menos
27/30. Há só dois rótulos humanos negativos, de modo que a taxa por classe
negativa não é estável. Um classificador que sempre desse 1 teria 28/30 de
concordância nesta amostra. A matriz importa justamente por isso.

## Oito desacordos

Classificação diagnóstica após a rodada. Nenhum rótulo original foi
alterado e a concordância não foi recalculada.

| Caso | Humano / Juiz | Classificação | Por quê |
|---|---|---|---|
| p2-04 | 1 / 0 | Defeito da rubrica | A resposta mistura falta de preço na base e pergunta imprecisa, sem dizer qual se aplica. A rubrica não exemplifica quando um limite genérico é explicação suficiente. |
| p2-05 | 1 / 0 | Defeito da rubrica | O pedido de consumo é específico, mas o texto pode soar como pedido de esclarecer. A rubrica não separa ausência explícita de dado de recusa com causa ambígua. |
| 17 | 0 / 1 | Defeito do rótulo humano | A justificativa humana julga se o câmbio é igual nos dois anos. A propriedade avaliada exclui precisão técnica e o texto orienta escolher um único ano. |
| 18 | 1 / 0 | Defeito do juiz | A recusa explica o escopo automotivo e por que não há próximo passo nesse canal. O juiz exigiu um passo mesmo assim. |
| 19 | 1 / 0 | Defeito do juiz | A resposta informa que não achou fonte e que só usa a base do LuxCar. O juiz ignorou a explicação de por que a consulta não pode seguir. |
| 20 | 1 / 0 | Defeito da rubrica | O texto não distingue quilometragem ausente de falta de especificação. Falta um exemplo que estabeleça se esse limite genérico basta. |
| 29 | 1 / 0 | Defeito do juiz | O próprio parecer reconhece que não há próximo passo porque a base não tem autonomia, mas a nota contradiz esse motivo aceito pela rubrica. |
| 30 | 1 / 0 | Defeito do juiz | A recusa identifica escopo e limite do canal. O juiz penalizou apenas a falta de instrução de próximo passo. |

Próxima rodada: versionar a rubrica com exemplos de recusa terminal e de
resposta genérica ambígua, calibrar os revisores para não misturar clareza
com exatidão e usar uma nova amostra com mais saídas negativas. O resultado
desta rodada continua 73,3%.
