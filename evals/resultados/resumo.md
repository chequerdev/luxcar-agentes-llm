# Resultados experimentais — LuxCar

**Importante:** verificação por regras é parcial; `revisar` não é aprovação. Isto não substitui juiz LLM validado com 30 rótulos humanos.

## Carimbo de reprodução

- **data_utc:** 2026-10-09T23:28:33.527049+00:00
- **modelo:** openai/gpt-oss-20b
- **provider:** Groq (OpenAI-compatible)
- **modo:** full
- **versoes:** A=prompt original; B=prompt original + regras 10
- **dataset_versao:** 1.0.0
- **dataset_sha256:** 731df82bdc1b933111e046837dd31692d2705c8599495a8c2336d33d9465694a
- **base_sha256:** c486e1b098e055b2eaba2ef188d65d49ff0b989b7b244d883dae147b746f4556
- **repeticoes_por_versao:** 2
- **temperatura:** não fixada; default do provedor
- **max_passos:** 5
- **rubrica:** regras locais v1; juiz LLM pendente
- **delay_s:** 3.0

## Métricas por versão e classe

| Versão | Classe | N | Aprovado | Falhou | Revisar | Erro | Cobertura trajetória | Efeito lateral OK |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| A | borda_divergencia | 6 | 4 | 2 | 0 | 0 | 4/6 | 6/6 |
| A | consulta_exata | 14 | 10 | 3 | 0 | 1 | 14/14 | 13/14 |
| A | incompleta | 8 | 4 | 0 | 4 | 0 | 8/8 | 8/8 |
| A | recusa_ausencia | 12 | 5 | 3 | 4 | 0 | 12/12 | 12/12 |
| B | borda_divergencia | 6 | 5 | 1 | 0 | 0 | 6/6 | 6/6 |
| B | consulta_exata | 14 | 12 | 2 | 0 | 0 | 14/14 | 14/14 |
| B | incompleta | 8 | 4 | 0 | 4 | 0 | 8/8 | 8/8 |
| B | recusa_ausencia | 12 | 6 | 2 | 4 | 0 | 12/12 | 12/12 |

## Ruído da versão A

Comparar as duas repetições A por caso: diferença na resposta, ferramentas ou regra. Mudanças A/B não devem ser promovidas se o ganho não superar o ruído de base.

- Casos A com duas repetições: **20**
- Casos com divergência de regra ou trajetória: **6**
- IDs divergentes: 01, 04, 05, 08, 09, 12

## Pendências para entrega final

1. Revisar manualmente casos sintéticos e respostas inconclusivas.
2. Validar um juiz LLM contra pelo menos 30 respostas rotuladas por humano, incluindo matriz de confusão e análise de desacordos.
3. Registrar previamente limiares e regra de promoção; avaliar se versão B supera A além do ruído observado.
4. Registrar versões de código, base, dataset, rubrica e parâmetros efetivos da API.
