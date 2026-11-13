# LuxCar | Base de conhecimento v1

## Fontes e responsabilidade

| Fonte versionada | Uso | Origem e limite |
|---|---|---|
| `dados/veiculos.json` | ID, marca, modelo, ano, versão e ficha de referência | Catálogo acadêmico simulado; não equivale a ficha homologada |
| `dados/estoque-demo.json` | Disponibilidade e mínimo comercial em centavos | Preços e situação fictícios atribuídos ao mesmo ID do catálogo |
| SQLite `revisoes` | Proposta em revisão, vendedor e validade | Estado operacional local; não representa uma reserva |
| SQLite `propostas` | Proposta ativa e valor confirmado | Estado operacional local, fonte decisiva para conflito |
| `dados/corpus/politicas-v2.json` | Busca documental do fluxo histórico | Corpus simulado. A versão revogada permanece apenas para teste histórico |

## Qualidade e vigência

O ID positivo e único identifica uma unidade, não apenas um modelo. O estoque e o catálogo devem ter o mesmo conjunto de IDs. Status aceitos: disponível, vendido e bloqueado. O valor mínimo deve ser positivo. A camada de acesso valida o formato e os campos obrigatórios antes de tomar a decisão. Arquivo ausente, JSON inválido, dados incompletos e erro SQLite produzem uma falha explícita no fluxo comercial. A validação é repetida na confirmação.

Os arquivos de demonstração devem ser alterados juntos, fora de uma execução ativa. Em produção, estoque, regras de preço e negociação precisariam de uma fonte transacional comum. Placa, CPF, telefone e dados do cliente não fazem parte da base comercial. Para auditar uma alteração de regra, atualize o caso correspondente em `evals/negociacao-casos.json` e rode o verificador novamente.
