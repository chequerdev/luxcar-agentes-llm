# Avaliação | Parte 3

A suíte chama as mesmas funções run_agent e resume_agent usadas por
python -m src.main, com SQLite descartável. O [conjunto 2.0.0](../evals/golden_dataset_v2.0.0.json)
tem 30 casos em cinco classes, 7 de desenvolvimento (todos os cenários da
Parte 2) e 23 sintéticos, incluindo recusas. Não há dados de produção.
**LACUNA:** os integrantes ainda precisam revisar e assinar os casos sintéticos.

| Propriedade | Nível | Como se confere | Por que não um nível mais barato |
|---|---|---|---|
| Estado, recusa e ficha | Determinístico | Contrato, status e trecho esperado | Já é o mais barato |
| Fonte consultada | Trajetória | Ferramenta esperada na execução | Texto não prova consulta |
| Uma escrita após revisão | Resultado | SQLite antes da aprovação e depois da decisão e da repetição; confere edição persistida | Trajetória não prova estado final |
| Clareza do próximo passo | Juiz LLM | Rubrica binária e nota estruturada | Palavras-chave não detectam instrução contraditória ou ambígua |

## Duas rodadas

A [anterior](../evals/resultados/parte3-anterior/resumo.json) obteve **26/30**
e a [nova](../evals/resultados/parte3-nova/resumo.json) **30/30**, +13,3 pontos
percentuais no mesmo conjunto e modo local. Mudaram quatro resultados:
registro de interesse para veículo inexistente, dois valores de potência
sem unidade e pergunta de câmbio sem identificação. Não são números de LLM.

## Juiz

A [rubrica](../evals/juiz/rubrica-v1.0.0.md) fixa limiar de 90% antes da
medição. O [CSV](../evals/juiz/rotulos-a-preencher.csv) contém saídas reais,
sem rótulos atribuídos. Os integrantes devem registrar rótulo binário, nome
e uma justificativa por saída. **LACUNA:** faltam 20 rótulos humanos,
execução do juiz com chave, matriz e classificação dos desacordos. Não
há concordância reportada, e o juiz não foi adotado.

    python -m evals.validar_juiz medir ROTULOS_REVISADOS.csv resultado-juiz.json
