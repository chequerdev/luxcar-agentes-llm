# Mudanças desde a Parte 2

O grafo, o estado, o RAG, a memória e a revisão humana da Parte 2 continuam
sendo usados. Referência da entrega anterior: c473beb. Base da Parte 3:
340a6e8. A devolutiva específica da Parte 2 não foi fornecida para conferência.

O commit `6a358b8` adicionou a suíte, os spans e os controles.
A [rodada anterior](../evals/resultados/parte3-anterior/) revelou proposta
para veículo inexistente, duas potências sem unidade e pergunta de câmbio
sem identificação tratada como fora de escopo. A
[rodada nova](../evals/resultados/parte3-nova/) reproduz as correções.
Também foram adicionados suspensão, restrição de edição e memória episódica
tipada. A [avaliação](evals.md) documenta as evidências e lacunas.


| Commit | Mudança e evidência |
|---|---|
| `9c4fc20` | Fechamento das conexões SQLite antes da limpeza da suíte no Windows. |
| `5f234b4` e `92eed2d` | Tentativas limitadas e retomada do juiz para limite da API e JSON inválido. |
| `edb59de` | [Validação do juiz](../evals/resultados/juiz-v1.0.0/analise.md), não adotado após 22/30 acordos. |
| `1c04025` e `caadbf3` | Correção de duas falhas de triagem e [comparação remota](../evals/resultados/parte3-groq-3.0.1/analise.md). |
| `4fbc623` | [Revisão dos casos sintéticos](revisao-sinteticos.md) e [trace documental](../evals/resultados/parte3-corpus-local-3.0.1/analise.md). |
