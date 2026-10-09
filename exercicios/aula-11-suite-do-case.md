# Exercício 11 — Suíte do case LuxCar (preparação)

**Estado:** planejamento pronto; execução e resultados pendentes. Este documento NÃO comprova que a suíte já rodou.

## 1. Dataset e origem

Arquivo: `evals/golden_dataset_v1.0.0.json`, com 20 casos distribuídos em cinco classes. Casos 01 e 02 se baseiam em demonstrações anteriores; os demais são sintéticos propostos, e precisam de revisão e identificação nominal dos revisores pelo grupo antes de uso. Não há casos de produção confirmados. Respostas esperadas dependentes do JSON devem ser verificadas contra uma cópia congelada de `dados/veiculos.json`.

## 2. Níveis e justificativa

| Propriedade | Nível escolhido | Por que não no nível mais barato |
|---|---|---|
| Campo de câmbio coincide com base | Determinístico | Igualdade com dado estruturado basta |
| Recusa de registro inexistente | Determinístico | Rótulo/critério objetivo basta, com inspeção manual se linguagem variar |
| Consulta a `buscar_veiculo` antes de responder | Trajetória | Resposta correta pode ter vindo de palpite; texto não prova consulta |
| `listar_versoes` nos casos de versões | Trajetória | Resposta não revela qual ferramenta foi usada |
| Cobertura, chamadas supérfluas e ordem | Trajetória | Exigem trace completo; checar apenas a resposta não basta |
| Histórico gravado exatamente uma vez | Resultado | Só inspeção do arquivo persistido detecta duplicação ou falsa confirmação |
| Base de veículos não alterada | Resultado | Precisa comparar arquivo antes/depois |
| Explicação sem afirmação técnica não sustentada | Juiz LLM | Expressões regulares não capturam toda paráfrase ou inferência técnica |

## 3. Juiz e validação

**Rubrica v1.0.0:** `SIM` se toda afirmação técnica específica for sustentada pelo retorno da ferramenta e a ausência de dados for reconhecida; `NÃO` se houver característica inventada, contradição ou certeza indevida. Exemplo SIM: “Polo TSI 2018: câmbio automático de 6 velocidades”, quando consta na ferramenta. Exemplo NÃO: acrescentar “tração integral” sem evidência.

**Saída estruturada esperada:** `{"veredito":"sim|nao","justificativa":"texto curto"}`. Viés principal: verbosidade; não premiar resposta longa. Antes de adotar, duas pessoas do grupo rotularão 30 saídas reais independentemente, registrarão notas e consenso em `evals/rotulos_humanos_30.csv`. Limiar de concordância juiz × consenso: **90% (27/30)**, declarado em 09/10/2026. Sem execução, matriz e desacordos estão **pendentes**, não zerados. Cada desacordo será lido e classificado como defeito do juiz, rubrica ou rótulo humano.

| | Humano sim | Humano não |
|---|---|---|
| Juiz sim | PENDENTE | PENDENTE |
| Juiz não | PENDENTE | PENDENTE |

## 4. Ruído, repetições e regra de promoção

Congelar base, modelo, parâmetros, prompt, memória (se houver) e ambiente; registrar variação restante. Rodar **A duas vezes** antes de comparar; depois rodar **A e B cinco vezes por caso** (20 × 5 = 100 execuções por versão). Reportar taxa geral, `pass^5`, e por classe. O trace deverá medir cobertura, chamadas supérfluas e ordem separadamente.

**Regra pré-declarada em 09/10/2026, antes da comparação:** promover B apenas se o ganho médio for de **pelo menos 5 pontos percentuais E maior que a dispersão absoluta A1 × A2**, nenhuma classe cair mais que **5 pontos percentuais**, `pass^5` não cair e não surgir falha crítica nova (invenção de dado, exposição pessoal, gravação duplicada). Caso contrário, não promover. Se o resultado for inconclusivo, ampliar testes.

**Ruído A1:** PENDENTE. **Ruído A2:** PENDENTE. **Comparação A/B:** PENDENTE. **Decisão:** PENDENTE.

## 5. Carimbo da execução (13 campos)

| Campo | Valor antes de executar |
|---|---|
| 1. Commit do código | A preencher pelo `git rev-parse HEAD` |
| 2. Versão do prompt | A registrar: `prompts/luxcar-v1.md` + hash |
| 3. Modelo | `ministral-8b-2512` (confirmar no código) |
| 4. Parâmetros de geração | A extrair do código/retorno |
| 5. Versão da base | Hash de `dados/veiculos.json` |
| 6. Versão das ferramentas | Hash de `src/tools.py` |
| 7. Versão da arquitetura/fluxo | Commit + hash de `src/main.py` |
| 8. Memória | Memória longa não implementada na V1; registrar estado do histórico |
| 9. Recuperação documental/RAG | Não implementada na V1 |
| 10. Framework | SDK Mistral no código atual; versão do pacote a registrar |
| 11. Versão do dataset | `1.0.0` |
| 12. Versão da rubrica do juiz | `1.0.0` |
| 13. Data/ambiente de execução | A preencher quando rodar |

Os nomes exatos do carimbo de 13 campos precisam ser confrontados com as notas anteriores da disciplina antes da entrega final; esta é uma proposta operacional, não uma transcrição da rubrica do professor.

## 6. Próximas ações obrigatórias

1. Revisar e assinar os casos sintéticos e conferir o snapshot da base.
2. Implementar runner, avaliadores de trace e estado, e juiz LLM no repositório real.
3. Executar a versão A duas vezes e calcular o ruído.
4. Obter 30 saídas, rotular manualmente, validar juiz e ler todos os desacordos.
5. Rodar A e B repetidamente e preencher resultados reais por classe.
6. Consolidar resultados em `docs/evals.md` na Parte 3.
