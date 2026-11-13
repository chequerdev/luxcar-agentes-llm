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

## Rodada com a Groq

No mesmo conjunto e provedor, a [versão 3.0.0](../evals/resultados/parte3-groq-3.0.0/analise.md)
passou em **25/30** e a [versão 3.0.1](../evals/resultados/parte3-groq-3.0.1/analise.md)
em **28/30**, ganho de 10 pontos percentuais. Os casos 17 e 26 passaram
após os controles de triagem. O caso 20 também passou. As duas falhas
restantes foram rejeições do JSON da triagem remota, com fallback local
funcional que não contou como aprovação remota.

    python -m evals.comparar evals/resultados/parte3-groq-3.0.0 evals/resultados/parte3-groq-3.0.1

## Juiz

A [rubrica](../evals/juiz/rubrica-v1.0.0.md) fixou o limiar de 90%
antes da medição. O GPT-OSS 20B na Groq foi comparado com 30 avaliações
humanas, todas com justificativa. Houve **22/30 acordos (73,3%)**, abaixo
do limiar. O juiz **não foi adotado** e não altera a nota das duas rodadas
funcionais. A [matriz e a análise dos oito desacordos](../evals/resultados/juiz-v1.0.0/analise.md)
estão junto do [resultado bruto](../evals/resultados/juiz-v1.0.0/resultado-bruto.json)
e dos [rótulos](../evals/resultados/juiz-v1.0.0/rotulos-humanos.csv).
A validação remota do juiz não substitui a medição do agente em modo remoto.

    python -m evals.validar_juiz medir ROTULOS_REVISADOS.csv resultado-juiz.json
