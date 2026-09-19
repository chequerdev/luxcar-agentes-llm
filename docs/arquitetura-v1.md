# Arquitetura v1 — LuxCar

## 1. Visão geral

O LuxCar é um agente especializado em responder dúvidas sobre veículos a partir de uma base estruturada de dados.

O usuário realiza uma pergunta em linguagem natural. O modelo interpreta a solicitação e decide quando é necessário consultar a base de veículos. O código executa a ferramenta, devolve o resultado ao modelo e, ao final, registra a interação no histórico.

A arquitetura utiliza autonomia limitada: o modelo pode decidir quando consultar a ferramenta de busca, enquanto o código controla a execução, os limites e o registro da conversa.

---

## 2. Entrada

A entrada é uma pergunta em texto livre feita pelo usuário.

Exemplo:

> Qual câmbio o Polo TSI 2018 possui?

O usuário não precisa seguir um formulário rígido. A pergunta pode variar de acordo com a forma como a pessoa escreve.

---

## 3. Fluxo da execução

```text
1. ENTRADA
   Usuário envia uma pergunta
   [decide: CÓDIGO]

        ↓

2. INTERPRETAÇÃO
   Modelo identifica veículo, ano, versão e informação solicitada
   [decide: MODELO]

        ↓

3. CONSULTA
   Modelo solicita a ferramenta buscar_veiculo
   [decide: MODELO]
   Código executa a ferramenta
   [decide: CÓDIGO]

        ↓

4. TRATAMENTO
   Resultado da ferramenta retorna ao modelo
   [decide: MODELO]

        ↓

5. RESPOSTA
   Modelo gera a resposta utilizando os dados disponíveis
   [decide: MODELO]

        ↓

6. REGISTRO
   Código registra pergunta, resposta e ferramenta utilizada
   em logs/historico.jsonl
   [ESCRITA — reversível]
   [decide: CÓDIGO]

        ↓

7. RETORNO
   Resposta é apresentada ao usuário
   [decide: CÓDIGO]