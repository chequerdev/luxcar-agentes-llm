# Model card | LuxCar Parte 3

1. **Identificação.** LuxCar v3.0.0, grafo de consulta e interesse da Parte 2.
2. **Finalidade.** Consultar fichas/políticas simuladas e registrar interesse após revisão.
3. **Autoridade.** Consultar e preparar revisão. Limites e evidências abaixo.
4. **Ferramentas e integrações.** Catálogo, corpus textual, SQLite e SDK OpenAI.
5. **Modelo e provedor.** Configuráveis em src/config.py. Modo local não chama modelo.
6. **Dados.** Catálogo, políticas e contatos simulados. Não apto a dados reais.
7. **Avaliação.** 26/30 e 30/30 em duas [rodadas](evals.md). Juiz com 22/30 acordos (73,3%) e não adotado, abaixo de 90%. [Matriz e desacordos](../evals/resultados/juiz-v1.0.0/analise.md). **LACUNA:** revisão dos casos sintéticos e rodada remota do agente.
8. **Limites conhecidos.** Sem estoque real, venda, pagamento ou autenticação.
9. **Riscos aceitos.** Identidade declarada do operador em bancada. [Decisão e gatilho](seguranca.md).
10. **Supervisão humana.** Interrupt antes de escrita, prazo e edição restrita.
11. **Registro e retenção.** Evidência abaixo. Arquivo operacional acessível ao operador local e guardado por sete dias pela política de bancada. **LACUNA:** prazo manual, sem auditoria de acesso. Traces versionados são sintéticos.
12. **Histórico de mudanças.** [Mudanças e evidências](mudancas.md).

| Autoridade | Onde se aplica | Evidência |
|---|---|---|
| Só consultar catálogo e corpus | Código, sem ferramenta de consulta externa | Nós de recuperação em src/graph.py |
| Proibido vender, transferir e alterar estoque | Ausência de ferramenta | Grafo em src/graph.py |
| Uma escrita por revisão | Código e chave de idempotência SQLite | test_hitl_edit_and_repeated_resume_do_not_duplicate |
| Qualquer escrita exige humano, prazo e veículo válido | Código, src/graph.py:224, :249 e :282 | tests/test_parte3.py e tests/test_graph.py |
| Se controle reprova, não escreve | Código | Testes de veículo inexistente e edição proibida |
| Operador pode suspender | LUXCAR_SUSPENSO=1 no código | test_suspension_prevents_resume |
| Chave para inferência, banco local | SDK e arquivo SQLite | **LACUNA:** privilégios e teto de gasto no provedor não verificados |

## Decisão reconstruída

No [trace](../evals/resultados/parte3-nova/traces.jsonl), busque
edca7075294c4c5f5fd999f09b98d28b. A raiz é a retomada da sessão
suite-p2-06:rodada:p2-06, v3.0.0. O evento luxcar.revisao registra
operador-teste, hora e aprovação do interesse no Volkswagen Polo TSI 2018.
A raiz anterior da mesma sessão contém o pedido e a validação do veículo,
com término awaiting_human. O filho execute_tool registrar_interesse
mostra argumentos minimizados, chave de idempotência e ausência de escrita
anterior. A raiz terminou completed com status approved. Isso não prova
a identidade civil do revisor.

## Lacunas e correções propostas

- Revisar os casos sintéticos. Para nova tentativa de adoção do juiz, esclarecer a rubrica e validar com nova amostra.
- Rodar com provedor configurado e medir consumo/custo.
- Antes de produção, autenticar operadores, validar credencial e teto, automatizar expurgo e acesso.
