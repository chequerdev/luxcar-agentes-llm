# RAG e recuperação

## Resposta direta

O RAG documental do LuxCar é **busca textual**, e os veículos são **consulta estruturada**. Não há busca vetorial. “Os dois” aqui significa duas formas de recuperar, não dois bancos.

| Forma | Implementação | Responde |
|---|---|---|
| consulta estruturada | filtro normalizado sobre `dados/veiculos.json` | registro exato por modelo/ano/versão e seus atributos |
| busca textual | TF-IDF local sobre seções em `dados/corpus/*.json`, `k=3` | políticas, privacidade, atualidade e aprovação |

Não há chunking por caracteres: cada seção editorial é um chunk, porque as políticas têm tópicos curtos com fronteira explícita. `k=3` limita ruído; o caso simples usa uma única chamada. O contador `retrieval_calls` aparece em todas as saídas.

## Corpus

- `veiculos.json`: registros simulados, mantidos pelo administrador quando o catálogo muda;
- `politicas-v2.json`: política vigente, revisão mensal ou por mudança de processo;
- `politicas-v1-revogado.json`: documento propositalmente obsoleto.

O revogado afirma que interesse podia ser registrado sem aprovação. A busca consegue encontrá-lo, mas `current:false` impede usá-lo como sustentação. Isso mostra que ranking sozinho não resolve vigência; curadoria/metadado resolve.

## Dez perguntas de avaliação

| # | Pergunta | Forma | Trecho esperado |
|---:|---|---|---|
| 1 | Qual câmbio do Polo TSI 2018? | estruturada | `veiculo:1.cambio` |
| 2 | Qual motor do Golf GTI 2015? | estruturada | `veiculo:2.motor` |
| 3 | Qual potência do Audi A3 Ambition 2016? | estruturada | `veiculo:4.potencia_cv` |
| 4 | Quais versões do Polo 2018? | estruturada | registros Polo/2018 |
| 5 | O Polo dito “manual” é mesmo manual? | estruturada, exceção por divergência | `veiculo:1.cambio` |
| 6 | Posso registrar interesse sem aprovação? | textual, exceção por documento revogado | `politicas-v2#s3`; v1 não vale |
| 7 | O LuxCar consulta preço em tempo real? | textual | `politicas-v2#s1` |
| 8 | Por que preciso informar a versão? | textual | `politicas-v2#s2` |
| 9 | O LuxCar fornece CPF do dono? | textual | `politicas-v2#s4` |
| 10 | Qual consumo rodoviário do Polo 2018? | estruturada, resposta ausente | nenhum trecho; recusar |

Há duas exceções (#5 e #6) e uma ausência (#10). Testes: `tests/test_retrieval.py`. A execução #10 está em `logs/parte2-caso-05-fora-do-corpus.json`.

## Entrada no grafo

A recuperação é uma **ferramenta escolhida pela rota de triagem**: `vehicle_query` chama consulta estruturada, `document_query` chama busca textual e as demais rotas não buscam. Nos casos finais, 1–5 fizeram uma recuperação cada; 6 e 7 fizeram zero. Não houve busca inútil nas rotas de pausa/entrada incompleta.

