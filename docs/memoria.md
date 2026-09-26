# LuxCar — Memória do Agente

## 1. Objetivo

Este documento define a estratégia de memória do agente LuxCar, estabelecendo quais informações devem existir apenas durante uma execução, quais podem persistir entre execuções e em quais situações essas informações devem ser atualizadas ou removidas.

Na versão atual do LuxCar, o agente consulta uma base estruturada de veículos e registra seu histórico de execução. A arquitetura de memória descrita neste documento representa uma decisão de projeto para a evolução do sistema e não implica que todos os mecanismos descritos já estejam implementados.

As decisões foram divididas em dois grupos:

1. como o agente lembra;
2. como o agente esquece.

O objetivo é evitar que o LuxCar simplesmente armazene todas as informações indefinidamente, estabelecendo critérios claros para persistência, recuperação, atualização e remoção.

---

# 2. Decisão 1 — Como o agente lembra

## 2.1 Memória de curto e longo prazo

O LuxCar separará sua memória em dois níveis: curto prazo e longo prazo.

| Característica | Curto prazo | Longo prazo |
|---|---|---|
| O que é | Estado da execução atual do LuxCar | Informações que permanecem disponíveis entre diferentes execuções |
| Conteúdo | Pergunta atual, objetivo, mensagens, chamadas de ferramentas, argumentos, resultados das consultas, resposta parcial, número de passos e motivo de término | Interações anteriores relevantes, fatos persistentes e regras estáveis do agente |
| Persistido como | Checkpoint identificado pela execução | Índice, tabela/chave-valor e texto de instruções |
| Como é lido | Pela identificação da execução quando ela precisa ser retomada | Por relevância, chave ou carregamento das regras |
| Acesso | Identificador único da execução | Similaridade, chave ou regra carregada no prompt |
| Ciclo de vida | Existe enquanto a execução puder ser retomada e depois pode ser descartado | Pode atravessar várias execuções, respeitando regras de atualização, decaimento e remoção |

### Checkpoint da execução

O checkpoint deve representar o estado necessário para que uma execução do LuxCar possa continuar exatamente do ponto em que parou.

Cada checkpoint deverá possuir, no mínimo:

```text
id_execucao
pergunta_usuario
objetivo
mensagens_da_conversa
passo_atual
ferramentas_ja_chamadas
argumentos_das_ferramentas
resultados_das_ferramentas
efeitos_ja_executados
resposta_parcial
estado_atual
motivo_de_pausa
timestamp
```

O registro de `efeitos_ja_executados` é importante para impedir que uma operação seja aplicada novamente quando uma execução for retomada.

Por exemplo, se futuramente o LuxCar possuir uma ferramenta que altera o status de um veículo ou registra uma negociação, o checkpoint deverá registrar que essa operação já foi realizada.

Assim, uma retomada não poderá executar novamente a mesma alteração.

O checkpoint também permitirá três comportamentos importantes:

### Retomada

Uma execução interrompida poderá continuar sem repetir ferramentas ou efeitos colaterais já realizados.

### Aprovação humana

Caso uma operação futura exija aprovação humana, a execução poderá permanecer pausada e ser retomada horas depois utilizando seu identificador.

### Depuração

Um checkpoint defeituoso poderá ser carregado para reproduzir o estado que levou a uma resposta ou decisão incorreta.

---

# 3. Orçamento da janela de contexto

A janela de contexto do modelo é um recurso limitado.

No LuxCar, cinco fontes diferentes poderão disputar espaço na janela:

1. system prompt;
2. objetivo atual;
3. trajetória da execução;
4. trechos recuperados da base de conhecimento;
5. memória de longo prazo recuperada.

Para evitar truncamento imprevisível, o LuxCar adotará um orçamento explícito.

| Fonte | Teto planejado |
|---|---:|
| System prompt | 1.500 tokens |
| Objetivo e pergunta atual | 500 tokens |
| Trajetória da execução | 2.000 tokens |
| Trechos recuperados da base de conhecimento | 3.000 tokens |
| Memória de longo prazo recuperada | 1.500 tokens |
| **Total planejado** | **8.500 tokens** |

Esses valores representam limites de projeto e poderão ser ajustados posteriormente por meio de testes com o modelo efetivamente utilizado.

## 3.1 Prioridade de descarte

Caso o conteúdo ultrapasse o orçamento definido, o LuxCar não deverá simplesmente cortar o final da janela.

A ordem de redução será:

```text
1. memórias episódicas antigas e de baixa relevância
2. trechos recuperados com menor relevância
3. partes antigas da trajetória já resumidas
4. informações redundantes
```

O sistema deverá preservar prioritariamente:

```text
system prompt
objetivo atual
pergunta atual
estado atual da execução
resultados recentes das ferramentas
informações necessárias para a próxima decisão
```

O system prompt e as instruções essenciais não devem ser removidos automaticamente para abrir espaço.

A trajetória antiga poderá ser resumida quando necessário, desde que sejam preservados os resultados e efeitos relevantes para a continuidade da execução.

---

# 4. Memória de longo prazo

O LuxCar utilizará três categorias conceituais de memória de longo prazo: episódica, semântica e procedural.

| Tipo | O que guarda no LuxCar | Estrutura | Como é recuperada |
|---|---|---|---|
| Episódica | Interações anteriores relevantes, situações problemáticas, consultas e correções que possam ajudar em situações semelhantes | Índice por similaridade com metadados e timestamp | Busca por similaridade com a pergunta ou situação atual |
| Semântica | Fatos persistentes e estruturados que precisam ser recuperados de forma exata | Chave-valor ou tabela | Consulta por chave |
| Procedural | Regras de comportamento do agente, utilização das ferramentas, limites e políticas de resposta | Texto versionado utilizado no system prompt | Carregada no início da execução |

## 4.1 Memória episódica

A memória episódica registra experiências relevantes do agente.

Exemplo:

```text
Situação:
Usuário perguntou por um Volkswagen Polo 2018 sem informar a versão.

Comportamento:
O sistema identificou que a versão era necessária antes de responder uma
característica específica.

Resultado:
O agente solicitou esclarecimento ao usuário.

Timestamp:
2026-09-25
```

Uma experiência desse tipo poderá ser recuperada quando uma situação semelhante ocorrer.

Nem toda conversa será transformada em memória episódica. Apenas situações consideradas úteis segundo a política de escrita poderão persistir.

---

## 4.2 Memória semântica

A memória semântica guarda informações que precisam ser recuperadas de forma determinística.

Exemplos:

```text
marca + modelo + ano -> versões cadastradas

veículo + versão -> características cadastradas

identificador do veículo -> registro correspondente
```

Quando uma informação possui uma chave conhecida, ela não deverá ser recuperada por similaridade se puder ser obtida de forma exata.

Na arquitetura atual, parte desse papel já é atendida pela base estruturada:

```text
dados/veiculos.json
```

A evolução da memória deverá preservar essa separação entre informação estruturada e informação recuperada semanticamente.

---

## 4.3 Memória procedural

A memória procedural contém as regras de funcionamento do agente.

Exemplos:

```text
não inventar informações sobre veículos;

consultar a ferramenta quando uma informação depender da base;

considerar os dados retornados pela ferramenta como fonte do sistema;

informar quando um veículo não estiver cadastrado;

solicitar esclarecimento quando faltar uma informação essencial;

não atribuir ao veículo características que não foram retornadas pela fonte.
```

Essas regras deverão permanecer em texto versionado e fazer parte das instruções do agente.

Uma alteração procedural deverá gerar uma nova versão, permitindo identificar quais regras estavam ativas em determinada execução.

---

# 5. Política de escrita da memória

O modelo não terá liberdade irrestrita para transformar qualquer conteúdo de uma conversa em memória permanente.

A persistência será controlada pelo código e por regras explícitas.

## 5.1 Memória episódica

Por execução, o sistema poderá registrar no máximo:

```text
0 a 3 registros episódicos
```

Cada registro deverá ser curto, preferencialmente contendo:

```text
situação
ação
resultado
timestamp
origem
```

O tamanho planejado é de aproximadamente 100 a 300 palavras por registro.

## 5.2 Memória semântica

Novos fatos semânticos não deverão ser criados apenas porque o modelo afirmou alguma informação.

A escrita deverá ocorrer somente quando o dado possuir origem confiável e puder ser associado a uma chave.

## 5.3 Memória procedural

O agente não poderá alterar sozinho suas próprias regras permanentes.

Alterações procedurais deverão ocorrer por atualização controlada e versionada do prompt ou configuração correspondente.

Quando uma regra for alterada a partir de um problema observado, ela deverá ser generalizada e não conter informações desnecessárias sobre o usuário que originou o caso.

---

# 6. O que o LuxCar não guarda

A definição do que não será armazenado é parte essencial da estratégia de memória.

O LuxCar não deverá persistir informações apenas porque elas apareceram em uma conversa.

## 6.1 Credenciais e segredos

Não serão armazenados em memória:

```text
senhas
tokens
chaves de API
credenciais
segredos de autenticação
```

Esses dados não são necessários para a memória do agente e representam risco de segurança.

## 6.2 Dados pessoais desnecessários

Informações pessoais que não sejam necessárias para a função do agente não deverão ser armazenadas.

Exemplos:

```text
CPF
RG
endereço residencial
dados bancários
telefone
e-mail
```

Caso uma funcionalidade futura necessite de algum identificador, deverá ser armazenado apenas o mínimo necessário e de acordo com a finalidade da funcionalidade.

## 6.3 Conteúdo externo não verificado

Uma afirmação fornecida por um usuário não deverá automaticamente se tornar um fato permanente.

Por exemplo:

```text
"O Polo TSI 2018 tem câmbio de 8 marchas."
```

Essa frase não deverá ser gravada como conhecimento do LuxCar apenas porque foi enviada pelo usuário.

A memória durável deverá utilizar informações verificadas por uma fonte adequada.

## 6.4 Informações deriváveis

Informações que podem ser facilmente recalculadas não deverão ser persistidas sem necessidade.

Exemplos:

```text
quantidade de resultados de uma consulta;
contagens temporárias;
ordenações que podem ser reconstruídas;
resumos que podem ser recalculados a partir da fonte original.
```

Guardar dados deriváveis aumenta o risco de inconsistência quando a informação original muda.

## 6.5 Conversas completas sem necessidade

O sistema não deverá transformar automaticamente toda conversa em memória permanente.

Somente informações selecionadas pela política de escrita deverão atravessar execuções.

---

# 7. Decisão 2 — Como o agente esquece

O LuxCar considera três causas diferentes de esquecimento:

| Causa | O que aconteceu | O dado é apagado? | Momento da decisão |
|---|---|---|---|
| Contradição | O fato mudou e existe uma versão mais recente | Não necessariamente | Durante a leitura |
| Decaimento | O fato envelheceu | Sim ou é rebaixado | Em rotina de manutenção |
| Remoção | O titular solicitou a exclusão | Sim | Sob demanda |

Esses três casos não devem ser tratados como o mesmo problema.

---

# 8. Contradição

Uma contradição ocorre quando dois fatos foram verdadeiros em momentos diferentes.

No domínio automotivo, isso pode ocorrer principalmente com informações mutáveis.

## Exemplo 1 — preço de referência

```text
01/01/2026:
Preço de referência do veículo = R$ 100.000

01/06/2026:
Preço de referência do mesmo veículo = R$ 96.000
```

Os dois valores podem ter sido corretos nas respectivas datas.

## Exemplo 2 — status de disponibilidade

```text
10/09/2026:
Veículo = disponível

15/09/2026:
Veículo = vendido
```

Novamente, os dois fatos podem ser verdadeiros em datas diferentes.

A similaridade semântica, isoladamente, não determina qual registro representa o estado mais recente.

Por isso, todo fato mutável persistido deverá possuir um carimbo de tempo.

Exemplo:

```json
{
  "veiculo_id": "123",
  "status": "vendido",
  "timestamp": "2026-09-15T14:30:00"
}
```

Quando dois fatos responderem à mesma chave ou pergunta, o LuxCar utilizará deterministicamente:

```text
max(timestamp)
```

para selecionar o fato mais recente.

O desempate não será delegado ao modelo de linguagem.

## Registro do descarte

Quando um fato mais antigo for recuperado, mas ignorado devido a uma versão mais recente, o evento deverá aparecer no log.

Exemplo:

```text
Fato recuperado: status=disponível
Timestamp: 2026-09-10

Fato selecionado: status=vendido
Timestamp: 2026-09-15

Motivo do descarte:
registro mais recente disponível
```

Isso permite distinguir um fato que foi recuperado e rejeitado de um fato que nunca foi encontrado.

---

# 9. Decaimento

Algumas informações perdem utilidade mesmo sem existir uma contradição explícita.

Para a memória episódica do LuxCar será adotado inicialmente um período de:

```text
180 dias
```

Após esse período, registros episódicos que não tenham sido reutilizados ou considerados relevantes serão removidos da memória ativa.

A escolha de 180 dias busca evitar que situações antigas ocupem indefinidamente a memória e influenciem consultas futuras.

Para fatos com alta taxa de mudança, como preço ou disponibilidade, o prazo deverá ser menor ou a consulta deverá utilizar diretamente uma fonte atualizada.

Informações estruturais estáveis, como regras procedurais, não utilizarão o mesmo prazo.

## Efeito do decaimento

No caso da memória episódica, o registro expirado será removido da memória ativa.

Antes da remoção, poderão ser mantidas métricas agregadas que não contenham identificadores pessoais, caso sejam necessárias para avaliação do sistema.

O decaimento não substitui a remoção solicitada pelo titular. Uma solicitação explícita de remoção deve ser processada imediatamente, independentemente da idade do registro.

---

# 10. Remoção solicitada

Quando o titular de uma informação solicitar sua remoção, o dado deverá ser eliminado de todas as estruturas em que possa existir.

A remoção não poderá se limitar à memória que o sistema normalmente consulta.

## 10.1 Estruturas que devem ser verificadas

A operação deverá considerar:

```text
1. memória episódica;
2. memória semântica;
3. memória procedural;
4. checkpoints;
5. logs de execução;
6. histórico de conversas;
7. índices de busca ou similaridade;
8. metadados associados aos registros;
9. arquivos estruturados persistidos;
10. caches, caso existam.
```

No projeto atual, estruturas como:

```text
logs/historico.jsonl
dados/veiculos.json
```

também deverão ser consideradas quando contiverem o identificador objeto da solicitação.

O checkpoint merece atenção especial porque poderá conter argumentos enviados às ferramentas mesmo que a informação nunca tenha sido transformada em memória de longo prazo.

O mesmo ocorre com logs que armazenzem argumentos ou resultados das ferramentas.

A memória procedural também deverá ser verificada. Uma regra criada após um erro não poderá conter o nome, identificador ou informação pessoal desnecessária do usuário que originou o aprendizado.

---

# 11. Procedimento de remoção e verificação

A confirmação da remoção deverá ser independente do processo utilizado para apagar os registros.

O procedimento será:

```text
1. identificar o titular ou identificador a remover;

2. localizar todas as estruturas em que ele pode existir;

3. executar a remoção;

4. concluir ou atualizar os índices afetados;

5. executar uma varredura independente em todas as estruturas;

6. procurar novamente o identificador removido;

7. registrar o resultado da verificação.
```

Exemplo:

```text
Identificador procurado:
cliente_123

Memória episódica: 0 ocorrências
Memória semântica: 0 ocorrências
Memória procedural: 0 ocorrências
Checkpoints: 0 ocorrências
Logs: 0 ocorrências
Histórico: 0 ocorrências
Índice: 0 ocorrências
Cache: 0 ocorrências

Resultado:
remoção verificada
```

A operação somente poderá ser considerada concluída após a varredura.

Caso a tecnologia de índice utilizada futuramente não permita remoção individual confiável, o índice deverá ser reconstruído sem os registros correspondentes.

Essa limitação deverá ser documentada porque afeta o tempo necessário para concluir a remoção.

---

# 12. Impacto da memória na reprodutibilidade

A adoção de memória de longo prazo significa que duas execuções aparentemente iguais podem produzir respostas diferentes em momentos diferentes.

Por exemplo:

```text
Execução A:
25/09/2026

Execução B:
25/10/2026
```

Mesmo utilizando:

```text
mesma pergunta
mesmo modelo
mesmos parâmetros
```

a resposta poderá mudar porque:

- novos fatos foram armazenados;
- registros antigos sofreram decaimento;
- uma contradição passou a possuir uma versão mais recente;
- uma informação foi removida;
- uma regra procedural foi atualizada.

Portanto:

```text
entrada + modelo + parâmetros
```

não são suficientes para reproduzir completamente uma execução.

Também será necessário conhecer:

```text
versão da memória
estado recuperado
versão do prompt
timestamp da execução
fontes recuperadas
checkpoint correspondente
```

Essa consequência é aceita como parte da arquitetura escolhida.

Nos testes futuros, será necessário controlar ou registrar o estado da memória para separar erros causados pelo modelo de erros causados pelo conteúdo armazenado.

---

# 13. Resposta à questão do exercício

## O que o LuxCar não guarda?

O LuxCar não guarda indiscriminadamente tudo o que aparece em uma conversa.

Não devem ser persistidos:

- credenciais e chaves de API;
- dados pessoais sem necessidade;
- conteúdo externo não verificado;
- afirmações do usuário tratadas automaticamente como fatos;
- informações facilmente deriváveis;
- conversas completas sem justificativa;
- estados temporários depois que deixarem de ser necessários.

## O que o LuxCar perde quando esquece?

O efeito depende da causa.

Na contradição, o sistema não precisa apagar o fato histórico, mas deixa de utilizá-lo como representação do estado atual e seleciona deterministicamente a versão mais recente.

No decaimento, experiências antigas podem ser removidas da memória ativa. Com isso, o agente perde a possibilidade de utilizar diretamente aquela experiência específica em situações futuras.

Na remoção solicitada, todas as informações relacionadas ao identificador devem ser eliminadas das estruturas abrangidas pela solicitação. O sistema perde deliberadamente a capacidade de recuperar aquela informação.

Essa perda é intencional: uma memória útil não é aquela que guarda tudo indefinidamente, mas aquela que possui critérios explícitos para decidir o que lembrar e o que esquecer.