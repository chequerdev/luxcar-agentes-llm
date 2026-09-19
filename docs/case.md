# LuxCar — Case v1

## 1. O problema

Usuários interessados em veículos precisam encontrar informações específicas sobre modelos, anos e versões, mas essas informações podem variar entre diferentes configurações do mesmo veículo e nem sempre estão disponíveis em um único local.

**Problema em uma frase:**  
> O usuário precisa de uma forma simples de consultar informações específicas de veículos sem precisar conhecer previamente a estrutura da base de dados ou pesquisar manualmente em diferentes fontes.

**Usuário principal:** cliente interessado em consultar informações sobre veículos.

### Contexto do problema

O problema ocorre quando o usuário deseja obter rapidamente uma informação específica sobre determinado veículo, como motorização, transmissão, potência, torque, combustível ou equipamentos.

Sem o LuxCar, o usuário precisa pesquisar essas informações manualmente em diferentes fontes e identificar corretamente o ano e a versão do veículo antes de confirmar se a informação encontrada corresponde ao modelo desejado.

Os principais casos que podem gerar erro são:

- ausência do ano do veículo;
- ausência da versão;
- diferentes versões do mesmo modelo;
- informações contraditórias fornecidas pelo usuário;
- consulta a um veículo que não está registrado na base;
- perguntas que não pertencem ao domínio de veículos.

---

## 2. Contexto

O LuxCar será utilizado como um chat de consulta sobre veículos.

O usuário inicia a conversa e envia uma pergunta em linguagem natural. O agente interpreta a pergunta, identifica as informações necessárias sobre o veículo, consulta a base estruturada disponível e produz uma resposta objetiva.

Na primeira versão, a base de dados utilizada pelo agente é **simulada**, armazenada em arquivo JSON e acessada por meio da camada de ferramentas do sistema.

### Onde o sistema é utilizado

O sistema funciona como uma interface de consulta em linguagem natural.

O usuário não precisa preencher campos específicos ou conhecer previamente a estrutura da base. Ele pode formular a pergunta livremente.

### O que existe antes e depois

**Antes:**

O usuário possui uma dúvida sobre determinado veículo.

**Entrada:**

Mensagem de texto livre enviada pelo usuário.

**Processamento:**

1. interpretação da pergunta;
2. identificação do veículo e do assunto;
3. verificação das informações necessárias;
4. consulta à base estruturada;
5. tratamento do resultado;
6. geração da resposta;
7. registro da conversa.

**Depois:**

O usuário recebe uma resposta textual no próprio chat.

**Consumidor da saída:**

O próprio usuário.

### Como o problema é resolvido atualmente

Sem o LuxCar, o usuário precisa pesquisar manualmente em diferentes fontes, localizar o veículo correto e confirmar se a informação encontrada corresponde ao ano e à versão desejados.

O tempo necessário para essa tarefa ainda será medido por meio de uma linha de base com perguntas representativas.

### Regras do domínio

As informações consideradas pelo sistema podem incluir:

- marca;
- modelo;
- ano;
- versão;
- motorização;
- transmissão;
- potência;
- torque;
- combustível;
- equipamentos;
- outras características presentes na base.

O agente deve seguir as seguintes regras:

1. Não inventar informações que não estejam disponíveis na fonte consultada.
2. Utilizar os dados retornados pelas ferramentas como fonte para a resposta.
3. Solicitar esclarecimentos quando as informações fornecidas forem insuficientes para identificar o veículo.
4. Informar quando o veículo ou versão consultada não estiver registrada.
5. Não responder perguntas fora do domínio de veículos como se possuísse conhecimento específico sobre elas.
6. Quando houver divergência entre uma informação fornecida pelo usuário e a informação retornada pela base, utilizar o dado registrado na base.

### Casos difíceis

A primeira versão considera quatro situações principais:

1. **Informação incompleta**  
   Exemplo: "Qual câmbio ele usa?", sem identificação suficiente do veículo.

2. **Divergência**  
   O usuário informa uma característica diferente daquela encontrada na base.

3. **Registro inexistente**  
   O usuário consulta um veículo, ano ou versão que não está presente na base simulada.

4. **Fora do escopo**  
   O usuário faz uma pergunta que não corresponde a uma consulta sobre veículos.

Esses casos serão utilizados nos testes do agente.

---

## 3. Usuários e interação

O sistema possui dois perfis principais.

| Perfil | O que quer | O que sabe | O que pode fazer |
|---|---|---|---|
| Cliente | Obter informações sobre veículos | Pode conhecer pouco ou muito sobre automóveis | Fazer perguntas, fornecer esclarecimentos e corrigir informações |
| Administrador da base | Manter os registros utilizados pelo sistema | Conhece os dados e a estrutura da base | Cadastrar, alterar e remover registros de veículos |

**Usuário principal:** cliente.

### Canal

A interação acontece por meio de um **chat textual**.

O usuário pode escrever perguntas em linguagem natural, sem precisar seguir um formato rígido.

### Quem inicia a interação

O usuário inicia a conversa e envia a pergunta.

O LuxCar não realiza interações proativas nesta versão.

### Quantidade de trocas

Quando a pergunta contém informações suficientes, o objetivo é:

```text
1 pergunta → 1 resposta