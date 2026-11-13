# Segurança | Parte 3

Canais não confiáveis: entrada do usuário, trecho recuperado, retorno de
ferramenta, memória recuperada e resposta do provedor. Não há MCP,
multiagente, mídia ou execução de código recebido.

| Impacto | Risco e ponto | Cenário | Mitigação |
|---:|---|---|---|
| 3 | ASI02, src/graph.py:224 | Operador solicita interesse em veículo fora do catálogo | Validar veículo único antes da revisão |
| 3 | ASI03, src/graph.py:249 | Revisor tenta alterar o veículo no formulário de aprovação | Edição restrita e prazo; sem aprovação, sem escrita |
| 2 | ASI06, src/memory.py:78 | Conteúdo externo vira memória persistente sem verificação | Episódio gravado pelo grafo usa ID e atributo tipados |
| 2 | ASI01, src/graph.py:81 | Mensagem induz o modelo a escolher outra rota | Contrato de triagem e portões fora do modelo; erro de leitura ainda possível |
| 2 | ASI09, src/main.py:49 | Revisor confunde ID do CLI com identidade autenticada | Risco aceito em bancada |
| 2 | ASI04, requirements.txt | Distribuição comprometida ou corpus não revisado entra no ambiente | Versões fixas e corpus versionado; sem verificação criptográfica das distribuições |

| Controle e local | Teste e falha | O que deixou de fazer |
|---|---|---|
| Catálogo exige veículo único, src/graph.py:224 | test_inexistent_vehicle_cannot_reach_approval, fail-closed | Não abre revisão para veículo futuro ou ausente |
| Edição restrita e aprovação, src/graph.py:249 | test_edit_cannot_change_vehicle e testes de repetição/prazo, fail-closed | Trocar carro exige novo pedido |
| Memória tipada, src/memory.py:78 | test_memory_entry_accepts_only_structured_reference, fail-closed | Não guarda resumo livre nem preferência inferida |
| Suspensão, src/main.py:35 e :49 | test_suspension_prevents_resume, fail-closed | Suspende consultas e revisões abertas |

**Risco aceito:** identidade declarada no CLI, sem autenticação. Limite:
bancada local, dados fictícios, sem acesso externo. Reavaliar antes de
abrir o terminal a terceiros ou conectar dados reais.

## Dados pessoais

| Local | Dados, finalidade e guarda |
|---|---|
| Entrada e checkpoint | Texto e contato fictícios permitem retomar revisão. Base do art. 7º não se aplica ao dado simulado. Não usar dados reais. Sem expurgo automático. |
| Prompt e provedor | Mensagem truncada, com sequência numérica longa minimizada, para triagem. Não recebe memória. A limpeza não é DLP completo. Retenção remota não verificada. |
| Índice | Política e ficha simuladas, versionadas, sem cadastro de clientes. |
| Memória episódica | Sessão, ID de veículo e atributo enumerado. O grafo não grava texto externo nesse caminho. Remoção local via scripts/remover_usuario.py. |
| Ação e trace | A ação histórica pode persistir telefone fictício. Trace omite contato em aprovação/escrita. Prazo operacional proposto de sete dias, remoção manual pelo operador. Evidência sintética versionada não expira. |

Para dados reais, falta estabelecer hipótese legal do art. 7º, acesso e
guarda. Não se assume autorização de tratamento.

## Histórico

git log --all -- .env não retornou linhas. A busca literal por
OPENAI_API_KEY= retornou 063cab8, que só adicionou o nome com valor vazio
em .env.example. A busca excluindo esse arquivo ficou vazia. Esse achado
não identificou valor de chave a revogar.
