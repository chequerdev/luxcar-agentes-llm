# LuxCar — Agente de IA

Trabalho acadêmico da disciplina de Agentes de IA / LLM.

O LuxCar é um agente especializado em responder dúvidas sobre veículos utilizando um modelo de linguagem e uma base de dados simulada.

---

## 1. Sobre o projeto

O objetivo do LuxCar é permitir que o usuário faça perguntas sobre veículos utilizando linguagem natural.

O agente interpreta a pergunta, identifica as informações necessárias sobre o veículo e utiliza ferramentas para consultar a base de dados do sistema.

Exemplo:

> Qual câmbio o Polo TSI 2018 possui?

O agente identifica o veículo e consulta a base de dados para retornar a informação disponível.

---

## 2. O que o agente faz

Atualmente, o LuxCar consegue:

- Interpretar perguntas relacionadas a veículos;
- Identificar marca, modelo, ano e versão quando disponíveis;
- Consultar veículos na base de dados;
- Listar versões disponíveis de um veículo;
- Responder utilizando as informações retornadas pelas ferramentas;
- Informar quando um veículo não está cadastrado;
- Pedir esclarecimentos quando faltam informações necessárias;
- Identificar perguntas fora do escopo de veículos;
- Registrar as interações realizadas em um arquivo de histórico.

---

## 3. O que o agente não faz

Nesta primeira versão, o LuxCar:

- Não realiza compra ou venda de veículos;
- Não realiza negociações;
- Não altera os dados dos veículos;
- Não consulta dados externos em tempo real;
- Não fornece informações que não estejam disponíveis na base;
- Não responde perguntas fora do domínio de veículos;
- Não substitui uma consulta técnica ou oficial do fabricante.

---

## 4. Arquitetura

O funcionamento básico do agente segue o fluxo:

```text
Usuário
   |
   v
Pergunta em linguagem natural
   |
   v
Modelo de linguagem
   |
   +----> buscar_veiculo
   |
   +----> listar_versoes
   |
   v
Processamento do resultado
   |
   v
Resposta ao usuário
   |
   v
Registro da interação

O modelo de linguagem é responsável pela interpretação da solicitação e pela decisão de utilizar uma ferramenta.

As ferramentas são responsáveis pelo acesso aos dados estruturados.

Mais detalhes sobre a arquitetura estão disponíveis em:

docs/arquitetura-v1.md

5. Tecnologias utilizadas
Python
Mistral AI
API da Mistral
JSON
python-dotenv
Git e GitHub
6. Estrutura do projeto
luxcar-agentes-llm/
│
├── dados/
│   └── veiculos.json
│
├── docs/
│   ├── arquitetura-v1.md
│   ├── base-de-conhecimento-v1.md
│   ├── case.md
│   ├── fontes.md
│   └── modelos.md
│
├── logs/
│   ├── caso-01-simples.json
│   ├── caso-02-divergencia.json
│   ├── caso-03-inexistente.json
│   ├── caso-04-fora-escopo.json
│   └── historico.jsonl
│
├── prompts/
│   └── luxcar-v1.md
│
├── src/
│   ├── main.py
│   └── tools.py
│
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
7. Base de dados

A primeira versão utiliza uma base de dados simulada em formato JSON.

Arquivo:

dados/veiculos.json

A base contém informações estruturadas dos veículos, como:

Marca;
Modelo;
Versão;
Ano;
Motor;
Potência;
Torque;
Combustível;
Câmbio.

As ferramentas do agente acessam essa base para obter as informações necessárias para responder às perguntas.

8. Ferramentas

O agente possui ferramentas para acessar e registrar informações.

buscar_veiculo

Realiza a busca de um veículo específico considerando:

Marca;
Modelo;
Ano;
Versão.

Exemplo:

Volkswagen Polo TSI 2018

Retorno de exemplo:

Volkswagen Polo TSI 2018 possui câmbio automático de 6 velocidades.
listar_versoes

Lista as versões disponíveis para uma determinada combinação de:

Marca;
Modelo;
Ano.

É utilizada quando o usuário informa o veículo, mas não informa a versão.

Exemplo:

Qual versão do Polo 2018 existe?
registrar_conversa

Registra a interação realizada pelo agente no arquivo:

logs/historico.jsonl

O registro contém informações como:

Pergunta;
Resposta;
Ferramenta utilizada.
9. Regras do agente

O comportamento do LuxCar é orientado por um prompt de sistema.

Entre as principais regras estão:

Responder somente sobre veículos;
Utilizar as ferramentas quando precisar consultar informações;
Utilizar somente informações retornadas pelas ferramentas;
Não inventar informações;
Informar quando um veículo não estiver cadastrado;
Pedir esclarecimentos quando faltarem informações essenciais;
Considerar os dados da ferramenta como fonte oficial em caso de conflito;
Não atribuir características que não tenham sido retornadas pela ferramenta;
Responder de forma objetiva e em português.

O prompt utilizado pelo projeto está versionado em:

prompts/luxcar-v1.md
10. Como executar
10.1 Pré-requisitos

É necessário ter instalado:

Python 3;
Git;
Uma chave de API da Mistral.
10.2 Instalação das dependências

No terminal, dentro da pasta do projeto, execute:

pip install -r requirements.txt
10.3 Configuração da API

Crie um arquivo chamado:

.env

na raiz do projeto.

Adicione:

MISTRAL_API_KEY=sua_chave_aqui

O arquivo .env não deve ser enviado para o GitHub.

O projeto possui o arquivo:

.env.example

como modelo de configuração.

10.4 Executando o agente

No terminal, execute:

python src/main.py

O programa solicitará uma pergunta:

Usuário:

Digite a pergunta e pressione Enter.

11. Exemplo de execução

Entrada:

Qual câmbio o Polo TSI 2018 possui?

O agente identifica o veículo e chama a ferramenta:

[TOOL] buscar_veiculo
[ARGUMENTOS] {'marca': 'Volkswagen', 'modelo': 'Polo', 'ano': 2018, 'versao': 'TSI'}

Resposta:

LuxCar: O Volkswagen Polo TSI 2018 possui câmbio automático de 6 velocidades.
12. Tratamento de casos

A primeira versão do projeto foi testada considerando diferentes situações.

Caso 1 — Pergunta simples
Qual câmbio o Polo TSI 2018 possui?

O agente consulta a base e apresenta a informação encontrada.

Caso 2 — Divergência
O Polo TSI 2018 tem câmbio manual. Qual é o câmbio dele?

O agente utiliza os dados retornados pela ferramenta como fonte oficial e informa a informação cadastrada na base.

Caso 3 — Veículo inexistente
Qual câmbio o Golf R 2020 possui?

Quando o veículo não está cadastrado, o agente informa que não encontrou o registro na base.

Caso 4 — Fora do escopo
Qual é a previsão do tempo para amanhã?

O agente informa que a solicitação está fora do escopo do LuxCar.

Os registros desses testes estão disponíveis na pasta:

logs/
13. Limites da primeira versão

A primeira versão utiliza uma base simulada e possui escopo limitado.

O agente depende das informações disponíveis em:

dados/veiculos.json

Caso determinada informação não esteja cadastrada, o agente não deve inventá-la.

Também existe um limite de passos de execução definido no código:

MAX_PASSOS = 5

Esse limite evita que o agente fique executando chamadas indefinidamente.

14. Documentação

A documentação do projeto está organizada na pasta docs/.

Principais documentos:

docs/case.md — descrição do caso de uso;
docs/modelos.md — análise do modelo utilizado;
docs/fontes.md — fontes utilizadas na pesquisa;
docs/arquitetura-v1.md — arquitetura da primeira versão;
docs/base-de-conhecimento-v1.md — planejamento da base de conhecimento.
15. Evolução planejada

A primeira versão representa uma arquitetura inicial do agente.

Nas próximas etapas do projeto poderão ser incorporados recursos como:

RAG;
Memória;
MCP;
LangGraph;
Multiagentes;
Segurança;
Observabilidade;
Gerenciamento de custos.
