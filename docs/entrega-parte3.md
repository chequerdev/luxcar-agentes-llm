# Guia da entrega | LuxCar, Parte 3

| Critério | Evidência |
|---|---|
| Sistema da Parte 2 e mudanças | [Histórico de mudanças](mudancas.md), grafo e suíte no mesmo repositório |
| Avaliação | [Método e rodadas](evals.md), [23 gabaritos revisados](revisao-sinteticos.md) |
| Juiz | [30 rótulos, matriz e oito desacordos](../evals/resultados/juiz-v1.0.0/analise.md), decisão de não adotar |
| Governança | [Model card e reconstrução de aprovação](model-card.md) |
| Segurança | [Controles, custos e risco aceito](seguranca.md), testes fora do prompt |
| Observabilidade | [Métricas locais e remotas por versão](observabilidade.md), [trace documental](../evals/resultados/parte3-corpus-local-3.0.1/analise.md) |
| Reprodução e apresentação | [README](../README.md), [roteiro e demo](apresentacao.md) |

**Limites da evidência.** A versão remota 3.0.1 passou em 28/30.
Nos outros dois casos, a Groq rejeitou o JSON e o fallback local
respondeu corretamente, sem contar como sucesso remoto. Duas chamadas
não informaram tokens. A recuperação documental foi demonstrada em
modo local. O CLI usa identidade declarada em bancada, sem autenticação.
Não foi disponibilizada devolutiva específica da Parte 2 para conferência.

**Quando for entregar.** O trabalho está na branch trabalho-3. Se o
professor aceitar link da branch, use o README dessa branch. Se exigir
o link padrão do repositório, integre a branch à main antes de enviar e
confira o README no link final. O PowerPoint é para apresentação.
A documentação técnica da entrega está em Markdown no repositório.
