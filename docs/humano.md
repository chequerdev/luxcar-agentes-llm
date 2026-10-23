# Human-in-the-loop

Somente `registrar_interesse` pausa, pois grava solicitação persistente com contato. O perfil chamado é o **operador LuxCar**.

O `interrupt` mostra ação, argumentos, consequência, respostas `approve/reject/edit` e prazo de 24 horas. O checkpointer SQLite é obrigatório. Na retomada com `Command(resume=...)`, o nó reinicia; por isso nenhum efeito colateral ocorre antes do `interrupt`.

Sem resposta, a execução permanece pausada. Uma retomada depois de 24 horas segue para `expired` e grava zero ações. Não há aprovação automática.

## Idempotência comprovada

A chave é SHA-256 de usuário + conteúdo estável da ação; timestamp/revisor não entram. No caso 6:

1. o grafo pausou;
2. o operador aprovou editando o contato;
3. uma segunda aprovação foi enviada ao mesmo `thread_id`;
4. `action_rows_after_two_approvals` permaneceu **1**.

Evidência: `logs/parte2-caso-06-human-in-the-loop.json`. Teste: `test_hitl_edit_and_repeated_resume_do_not_duplicate`.

