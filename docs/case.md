# LuxCar | abertura de negociação

## 1. Problema e contexto

**O vendedor de um showroom precisa saber se pode abrir uma proposta antes que outro vendedor negocie o mesmo carro.**

1. **Onde e quem.** O vendedor inicia o fluxo no chat interno (protótipo no terminal). Não é um atendimento direto ao cliente.
2. **Antes e depois.** Antes, existe um veículo de interesse e, para registrar, um valor oferecido. Depois, o vendedor recebe a situação do estoque, uma revisão a confirmar, o ID de uma proposta gravada ou o motivo para não prosseguir.
3. **Como se resolve hoje.** O vendedor procura a ficha, confere a situação do estoque e as propostas ativas e verifica o mínimo comercial. Se não puder decidir, consulta o gerente. Não temos acesso a uma concessionária para cronometrar esse processo real. Para medir em bancada, execute o procedimento abaixo com as duas pessoas do grupo e registre os tempos individuais. Não trate bancada como medição de loja.
4. **Regras de negócio.** Uma unidade identificada pelo ID pode ter no máximo uma proposta ativa. Unidade vendida ou bloqueada não aceita proposta. O valor deve atingir o mínimo daquele veículo. Uma revisão não reserva o veículo e vence em 15 minutos. Só o vendedor que abriu a revisão confirma os dados da própria proposta. Exceções vão ao gerente, fora do agente.
5. **Casos difíceis.** Nome do A3 junto ao ID do Polo → pedir correção. Carro inexistente → não presumir disponibilidade. Valor abaixo do mínimo → gerente. Duas revisões concorrentes → só a primeira confirmação elegível grava. Consulta de disponibilidade → responde sem gravar.

### Linha de base manual

Para cada cenário de `evals/negociacao-casos.json`, use uma cópia nova do catálogo e do estoque com a lista de propostas vazia. Sem usar o agente, abra o cenário, localize o ID, confira status, proposta ativa e mínimo conforme aplicável e escreva a decisão. Cronometre da leitura do pedido até a decisão escrita. Não inclua o tempo de espera pela confirmação, que é humano em ambas as alternativas. Registre cenário, participante, segundos e decisão, e calcule a mediana dos tempos e o número de decisões certas. **Medição com participantes ainda pendente.**

## 2. Usuários e conversa

| Perfil | O que quer | O que sabe | O que pode fazer |
|---|---|---|---|
| Vendedor (principal) | Abrir proposta sem conflito | Veículo pretendido e valor ofertado | Consultar, solicitar, confirmar ou rejeitar a própria revisão |
| Gerente comercial | Resolver exceções de preço ou conflito | Regras e contexto de negociação | Decidir exceções manualmente, fora do agente |
| Responsável pelo estoque | Corrigir cadastro e indisponibilidade | Registro da unidade e status correto | Validar e corrigir a fonte fora do agente |

O vendedor começa por chat porque o pedido chega em linguagem natural durante o atendimento. Uma consulta costuma exigir um pedido e uma resposta. Um registro bem-sucedido exige duas trocas, pedido/revisão e confirmação/recibo. Quando há omissão ou contradição, o vendedor reenvia uma frase completa. Não há inferência a partir de um turno anterior. Suficiência significa um único veículo identificado e, para escrita, um valor explícito. A revisão contém ID, veículo, valor e validade. O final traz JSON com motivo, mensagem e, quando aplicável, ID persistido. A falha encerra a tentativa atual sem proposta e indica quem pode resolver. A interface é um protótipo de terminal e não autentica a identidade de um operador real.

Exemplo de diálogo completo (IDs abreviados):

> Vendedor — Abra uma proposta para o Polo.
>
> LuxCar — Informe o valor em reais.
>
> Vendedor — Abra uma proposta para o Polo por R$ 70.000,00.
>
> LuxCar — Revisão `abc…`, Volkswagen Polo TSI 2018, R$ 70.000,00. Confirme ou rejeite em até 15 minutos. Nenhuma proposta foi criada.
>
> Vendedor — Confirmo a revisão `abc…` no comando de confirmação.
>
> LuxCar — Proposta `abc…` registrada.

Não há ação irreversível automatizada neste protótipo. O registro comercial é persistente e exige confirmação. Um cancelamento administrativo pode liberar a unidade, mas a interface do agente não cancela, conclui vendas, cobra pagamentos ou envia mensagens.

## 3. Workflow

1. **Código** valida o vendedor de demonstração, a entrada e o orçamento.
2. **Modelo** escolhe uma das três ferramentas e extrai os argumentos. **Código** valida a escolha e não permite ampliar a autorização. No modo local, o código faz a seleção.
3. **Código** consulta a camada de catálogo/estoque, verifica conflito e mínimo quando aplicável. Se não houver uma ação elegível, encerra ou orienta encaminhamento.
4. **Código** grava a revisão pendente **[escrita reversível por rejeição/expiração]** e mostra veículo, valor e validade.
5. **Humano** confirma ou rejeita com o ID da revisão. Se não confirmar, não há proposta.
6. **Código** revalida em transação e grava uma única proposta ativa **[escrita comercial persistente, reversível administrativamente]**, ou devolve a causa do bloqueio.
7. **Código** registra a trajetória e o motivo de término **[escrita de log, reversível por retenção/remoção]** e devolve a saída estruturada. Isso acontece também nos fluxos encerrados antes da revisão.

## 4. Justificativa de negócio e verificador

O valor está em impedir que duas pessoas tratem a mesma unidade como livre e em preservar a decisão de quem realmente confirmou. A linguagem natural varia, mas a regra de conflito não. O modelo escolhe uma ação ou pede esclarecimento. O código aplica as regras e tem a última palavra sobre a escrita.

O verificador compara os rótulos fixos do conjunto `evals/negociacao-casos.json` com o motivo devolvido, a decisão após confirmação e o número de propostas no SQLite antes e depois. Cada caso começa com um banco isolado. **Meta inicial: 5/5 casos corretos e 0/5 com proposta antes da confirmação.** Os testes adicionais cobrem corrida, expiração, recusa, credencial de demonstração divergente e corrupção de fonte. Consulte `logs/negociacao/local/` para o resultado efetivamente obtido sem modelo.

## 5. Dados, maior risco e próximos passos

Catálogo e estoque são arquivos simulados versionados. O estoque de demonstração não se conecta ao TCC nem representa preço real de mercado. Use apenas identificadores fictícios de vendedor. Telefone, CPF, nome de cliente e placa seriam dados sensíveis para este fluxo e não são necessários. O texto original não é registrado no log comercial. A configuração remota envia a mensagem ao provedor, por isso não cole dados reais no terminal.

O maior risco é registrar duas propostas concorrentes ou registrar para o carro errado. Plano B: bloquear diante de conflito, divergência, fonte indisponível ou aprovação vencida e encaminhar ao gerente ou responsável pelo estoque. A transação e a restrição de unicidade são a proteção final contra concorrência. Próximo passo de produção: autenticar o vendedor, integrar o estoque oficial e definir cancelamento/auditoria com o gerente. O fluxo histórico de consulta técnica continua disponível separadamente.
