# Resultados experimentais — LuxCar

**Importante:** verificação por regras é parcial; `revisar` não é aprovação. Isto não substitui juiz LLM validado com 30 rótulos humanos.

## Carimbo de reprodução

- **data_utc:** 2026-10-23T03:50:24.251456+00:00
- **modelo:** openai/gpt-oss-20b
- **provider:** Groq (OpenAI-compatible)
- **modo:** smoke
- **versoes:** A=prompt original; B=prompt original + regras 10
- **dataset_versao:** 1.0.0
- **dataset_sha256:** 731df82bdc1b933111e046837dd31692d2705c8599495a8c2336d33d9465694a
- **base_sha256:** c486e1b098e055b2eaba2ef188d65d49ff0b989b7b244d883dae147b746f4556
- **repeticoes_por_versao:** 1
- **temperatura:** não fixada; default do provedor
- **max_passos:** 12
- **rubrica:** regras locais v1; juiz LLM pendente
- **delay_s:** 0.0

## Métricas por versão e classe

| Versão | Classe | N | Aprovado | Falhou | Revisar | Erro | Cobertura trajetória | Efeito lateral OK |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| A | consulta_exata | 1 | 1 | 0 | 0 | 0 | 1/1 | 1/1 |

## Ruído da versão A

Comparar as duas repetições A por caso: diferença na resposta, ferramentas ou regra. Mudanças A/B não devem ser promovidas se o ganho não superar o ruído de base.

- Casos A com duas repetições: **0**
- Casos com divergência de regra ou trajetória: **0**
- IDs divergentes: nenhum observado

## Pendências para entrega final

1. Revisar manualmente casos sintéticos e respostas inconclusivas.
2. Validar um juiz LLM contra pelo menos 30 respostas rotuladas por humano, incluindo matriz de confusão e análise de desacordos.
3. Registrar previamente limiares e regra de promoção; avaliar se versão B supera A além do ruído observado.
4. Registrar versões de código, base, dataset, rubrica e parâmetros efetivos da API.
