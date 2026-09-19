
---

# 3. `docs/base-de-conhecimento-v1.md`

Aqui eu **corrigi aquela parada da FIPE API**, porque descobrimos que a própria FIPE informa que não disponibiliza API oficial. E também deixei muito claro o que é **V1 atual** e o que é **planejamento futuro**.

```markdown
# LuxCar — Base de Conhecimento v1

## 1. Objetivo

A base de conhecimento do LuxCar tem como objetivo definir quais informações o agente poderá consultar, onde essas informações estão armazenadas e qual estratégia será utilizada para recuperar cada tipo de dado.

O objetivo principal é evitar que o modelo de linguagem precise depender exclusivamente de seu conhecimento interno para responder perguntas específicas sobre veículos.

Por exemplo, diante da pergunta:

> "Qual câmbio o Polo TSI 2018 possui?"

o agente deve consultar uma fonte do projeto antes de responder, em vez de simplesmente confiar na memória do modelo.

---

## 2. Tipos de conhecimento

O LuxCar trabalha com três categorias principais de informação.

### 2.1 Conhecimento geral

São informações gerais sobre automóveis que fazem parte do conhecimento do modelo de linguagem, como conceitos básicos de:

- motores;
- transmissões;
- tração;
- combustível;
- manutenção;
- componentes automotivos.

Esse conhecimento não precisa ser armazenado novamente na base do LuxCar.

### 2.2 Dados estruturados

São informações que possuem campos bem definidos e que podem ser consultadas diretamente.

Exemplos:

- marca;
- modelo;
- ano;
- versão;
- motor;
- potência;
- torque;
- combustível;
- transmissão;
- equipamentos;
- preço cadastrado;
- quilometragem;
- identificadores.

Na primeira versão, esses dados estão em:

```text
dados/veiculos.json