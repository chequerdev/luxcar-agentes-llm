# LuxCar — Model Card com evidências

**Versão do documento:** 1.0 (Exercício 12)  
**Data da revisão:** 16/10/2026  
**Sistema avaliado:** estado público da branch `main` do repositório `chequerdev/luxcar-agentes-llm` consultado em 16/10/2026.  
**Regra de leitura:** a referência `arquivo:Lx-Ly` aponta para linhas de código ou evidência versionada. Os links abaixo podem mudar com novos commits; **LACUNA L01**: fixar o SHA do commit auditado e registrá-lo neste cartão. O que é apenas intenção, configuração incompleta ou sem comprovação está expressamente marcado como **LACUNA**.

## 1. Identificação

**Afirmação.** LuxCar é um agente acadêmico para perguntas sobre características de veículos, em português. O documento descreve a implementação examinada em 16/10/2026; não é uma certificação de uso comercial. Responsável técnico indicado para o trabalho: **Gabriel Chequer de Oliveira**. A designação formal do responsável por incidentes, do suplente e de quem autoriza produção não está comprovada (**LACUNA L02**).

**Evidências:** [`README.md`](../README.md), seção “Sobre o projeto”; [`src/main.py:L92-L123`](../src/main.py); repositório: https://github.com/chequerdev/luxcar-agentes-llm.

## 2. Finalidade

**Afirmação.** O agente recebe uma pergunta em texto, identifica dados de marca/modelo/ano/versão quando aplicáveis, consulta a base simulada e apresenta uma resposta. Seus usuários previstos são alunos/testadores do protótipo. Não deve ser usado como laudo mecânico, decisão de crédito, precificação em tempo real, compra/venda de veículos nem consulta a cadastro pessoal. A ausência de ferramentas de transação ou acesso externo a cadastros reduz parte desse risco, mas as restrições à redação das respostas dependem de instrução ao modelo (**LACUNA L03**).

**Evidências:** [`src/main.py:L21-L90`](../src/main.py); [`src/main.py:L103-L117`](../src/main.py); [`src/tools.py:L4-L37`](../src/tools.py); [`README.md`](../README.md), seções 2 e 3.

## 3. Autoridade e ponto de aplicação

O LuxCar **pode consultar** o arquivo local de veículos, **pode listar** versões existentes e **pode registrar** pergunta e resposta em histórico local. As autorizações e limitações efetivas são:

| Regra / autoridade | Ponto de aplicação | Evidência | Estado |
|---|---|---|---|
| Consultar veículos e versões cadastrados | Código, funções locais que leem JSON | [`src/tools.py:L4-L37`](../src/tools.py), [`L61-L92`](../src/tools.py) | Evidenciado |
| Não efetuar pagamentos, comprar ou vender | Ausência de ferramenta de transação na lista entregue ao modelo | [`src/main.py:L21-L85`](../src/main.py) | Evidenciado para essa implementação; não impede mudanças futuras no código |
| Não alterar cadastro de veículos | Ferramentas de consulta somente leem `dados/veiculos.json` | [`src/tools.py:L14-L17`](../src/tools.py), [`L66-L68`](../src/tools.py) | Evidenciado no código das ferramentas; **LACUNA L04** para permissão de arquivo/sistema operacional |
| Registrar a conversa | Escrita local em `logs/historico.jsonl`, com modo `a` | [`src/tools.py:L39-L59`](../src/tools.py); [`src/main.py:L191-L195`](../src/main.py) | Evidenciado |
| Limitar a execução a cinco passos de requisição ao modelo | Código (`MAX_PASSOS=5` e condição do loop) | [`src/main.py:L19-L20`](../src/main.py); [`L136-L136`](../src/main.py); [`L182-L189`](../src/main.py) | Evidenciado; **LACUNA L05**: teste automatizado específico do limite e tratamento seguro ao atingir o teto |
| Responder apenas sobre veículos, não inventar informações e recusar outros assuntos | **Somente prompt** | [`src/main.py:L103-L117`](../src/main.py) | **LACUNA L03**: não há filtro determinístico garantindo a regra |
| Credencial externa | Chave `GROQ_API_KEY` carregada do ambiente e enviada ao cliente Groq | [`src/main.py:L7-L17`](../src/main.py); [`.gitignore`](../.gitignore) | Evidência de uso da chave; **LACUNA L06**: não há prova do escopo real, rotação ou restrições da credencial |
| Limite de gasto/consumo | Não foi identificada configuração de teto monetário no código | [`src/main.py:L14-L20`](../src/main.py) | **LACUNA L07**: comprovar limite na plataforma Groq e política de orçamento |
| Limiar de aprovação humana | Não existe etapa de aprovação humana no fluxo atual | [`src/main.py:L92-L205`](../src/main.py) | **LACUNA L08**: criar política de aprovação para casos sensíveis, se o escopo aumentar |
| Falha de controle | Chamada de ferramenta captura exceções; ausência de chave causa erro de inicialização | [`src/main.py:L9-L12`](../src/main.py); [`L146-L156`](../src/main.py) | **LACUNA L09**: regra geral de falha segura, suspensão e testes de exceção |
| Suspensão do agente | Operação local pelo terminal; não há mecanismo formal de bloqueio ou operador designado | [`src/main.py:L200-L205`](../src/main.py) | **LACUNA L10**: definir autorizados e procedimento reprodutível de suspensão |

**Revisão de privilégios.** A única integração remota identificada é a API Groq. A aplicação também escreve um arquivo local de histórico. Não foi identificada ferramenta MCP na lista registrada no código. A chave da Groq não demonstra permissão de acesso a sistemas financeiros ou ao banco de veículos, mas tampouco há auditoria documentada de escopo, permissões de conta e limites externos (**LACUNA L06**). Retirar privilégios excedentes da chave ou justificar sua manutenção antes de qualquer uso não acadêmico.

## 4. Ferramentas e integrações

| Ferramenta / serviço | Permissão efetiva identificada | Evidência |
|---|---|---|
| `buscar_veiculo` | Leitura local de `dados/veiculos.json` | [`src/tools.py:L4-L37`](../src/tools.py) |
| `listar_versoes` | Leitura local de `dados/veiculos.json` | [`src/tools.py:L61-L92`](../src/tools.py) |
| `registrar_conversa` | Escrita local em `logs/historico.jsonl`; não consta na lista de ferramentas expostas ao modelo, mas é chamada pelo programa | [`src/main.py:L21-L90`](../src/main.py), [`L191-L195`](../src/main.py); [`src/tools.py:L39-L59`](../src/tools.py) |
| API Groq (SDK compatível com OpenAI) | Envio ao provedor de mensagens, pergunta e, quando houver, resultados das ferramentas | [`src/main.py:L14-L19`](../src/main.py), [`L126-L132`](../src/main.py), [`L158-L178`](../src/main.py) |
| MCP | Nenhum servidor MCP integrado identificado no fluxo examinado | [`src/main.py:L1-L90`](../src/main.py); **LACUNA L11**: inventariar futuras integrações, caso adicionadas |

## 5. Modelo e provedor

**Afirmação.** O programa informa `MODEL = "openai/gpt-oss-20b"`, usando o endpoint `https://api.groq.com/openai/v1`. A avaliação do Exercício 11 registra o mesmo identificador e a data UTC `2026-10-09T23:28:33.527049+00:00`. O identificador de modelo **não prova sozinho** o snapshot exato dos pesos e da infraestrutura; não há revisão datada de implantação do modelo (**LACUNA L12**). Também não foram confirmados região de processamento, trânsito internacional, prazos de retenção contratual e condições específicas para uso de dados em treinamento (**LACUNA L13**). Não afirmar que os dados ficam no Brasil ou que não são usados para treino sem documentação do provedor e plano aplicável.

**Evidências:** [`src/main.py:L14-L20`](../src/main.py); [`evals/resultados/resumo.md`](../evals/resultados/resumo.md), “Carimbo de reprodução”.

## 6. Dados pessoais e inventário de fluxo

A base `dados/veiculos.json` foi construída para informações de veículos, mas **a pergunta livre do usuário pode conter nome, CPF, placa, telefone ou outro dado identificável**. O histórico grava a pergunta sem mascaramento; a pergunta também é enviada ao provedor no contexto do modelo. **Não assumir que todos os dados são anônimos.**

| Local: entrada, armazenamento ou saída | Dado e finalidade | Base legal LGPD (art. 7º) | Retenção / situação | Evidência |
|---|---|---|---|---|
| Entrada pelo terminal / prompt | Pergunta livre para responder ao usuário; pode incluir dado pessoal inserido espontaneamente | **LACUNA L14**: definir base legal aplicável antes de receber dados reais; eventual consentimento ou legítimo interesse exige avaliação específica | Temporário durante a execução; período em memória não documentado | [`src/main.py:L102-L123`](../src/main.py), [`L200-L205`](../src/main.py) |
| Contexto enviado à Groq | Pergunta, instruções e resultados de consulta para geração da resposta | **LACUNA L14**: fundamentar o compartilhamento e informar usuário | **LACUNA L13**: prazo e região no provedor não comprovados | [`src/main.py:L126-L132`](../src/main.py), [`L158-L178`](../src/main.py) |
| Base de veículos local | Marca, modelo, ano e ficha técnica, com propósito de consulta; nenhum dado de titular foi identificado no esquema descrito | Em princípio informações técnicas sem titulares identificados; **LACUNA L15**: varredura completa da base e futuros campos | Conservada no repositório sem política de eliminação | [`src/tools.py:L14-L37`](../src/tools.py); [`dados/veiculos.json`](../dados/veiculos.json) |
| Índice vetorial / RAG | Nenhuma implementação identificada no fluxo atual | Não se aplica enquanto inexistente | Não se aplica; **LACUNA L11** se incluído futuramente | [`src/main.py:L21-L90`](../src/main.py) |
| Memória persistente | Não há memória de perfil pessoal identificada; histórico de conversa constitui retenção local de interações | **LACUNA L14** para histórico contendo dados pessoais | **LACUNA L16**: prazo e exclusão ausentes | [`src/tools.py:L39-L59`](../src/tools.py) |
| Log de execução normal | Pergunta integral, resposta e última ferramenta utilizada, para histórico/depuração | **LACUNA L14**: base legal e necessidade dos dados completos | Prazo indeterminado no código (**LACUNA L16**) | [`src/tools.py:L39-L54`](../src/tools.py) |
| Saída do agente | Texto ao solicitante, que pode repetir dados fornecidos na entrada | **LACUNA L14**: controles adequados de privacidade | Não há política de retenção fora do log | [`src/main.py:L182-L205`](../src/main.py) |
| Avaliações | Perguntas sintéticas e rastros de ferramentas/resultados nos arquivos de avaliação; exemplos incluem CPF/placa como conteúdo de teste | Base legal necessária se forem incluídos dados pessoais reais (**LACUNA L14**) | **LACUNA L16**: política de retenção e acesso às evidências | [`evals/golden_dataset_v1.0.0.json`](../evals/golden_dataset_v1.0.0.json); [`evals/executar_suite.py:L84-L138`](../evals/executar_suite.py), [`L199-L210`](../evals/executar_suite.py) |

**Problemas de minimização identificados:** salvar o texto integral de todas as perguntas mesmo quando só o tipo de consulta seria suficiente; ausência de remoção automática, anonimização e controle de acesso documentados (**LACUNA L16**). **Ação recomendada:** para o exercício, usar somente perguntas sintéticas; para uso com pessoas, definir aviso de privacidade, base legal, retenção limitada e mascaramento de dados identificáveis antes de enviar ao modelo ou registrar.

## 7. Avaliação

**Afirmação.** Existe uma suíte local com dataset **v1.0.0, 20 casos**. A execução registrada em **09/10/2026**, modo `full`, avaliou quatro execuções por caso (duas da versão A e duas da B), totalizando **80 resultados**. A rubrica é automatizada por regras e separa `aprovado`, `falhou`, `revisar` e `erro`; isso **não** equivale a avaliação humana completa.

| Indicador | Versão A (40) | Versão B (40) |
|---|---:|---:|
| Aprovado pela regra | 23 | 27 |
| Falhou | 8 | 5 |
| Revisar | 8 | 8 |
| Erro | 1 | 0 |
| Cobertura de trajetória | 38/40 | 40/40 |

**Por fatia (aprovados / total):**

| Classe | A | B |
|---|---:|---:|
| Consulta exata | 10/14 | 12/14 |
| Incompleta | 4/8 | 4/8 |
| Borda / divergência | 4/6 | 5/6 |
| Recusa / ausência | 5/12 | 6/12 |

A versão A apresentou **6 casos com divergência de regra ou trajetória** nas duas repetições (IDs 01, 04, 05, 08, 09 e 12). A versão B melhorou a pontuação da rubrica, mas a promoção de versão não está aprovada por comparação validada. **LACUNA L17:** não foi demonstrada concordância de juiz LLM com ao menos 30 julgamentos humanos (matriz de confusão e desacordos), nem conclusão de revisão humana dos itens marcados `revisar`.

**Evidências:** [`evals/golden_dataset_v1.0.0.json`](../evals/golden_dataset_v1.0.0.json), `versao` e `casos`; [`evals/executar_suite.py:L27-L71`](../evals/executar_suite.py), [`L174-L213`](../evals/executar_suite.py); [`evals/resultados/resumo.md`](../evals/resultados/resumo.md), métricas por classe e pendências. Os resultados correspondem ao carimbo documentado, não a uma reexecução feita na elaboração deste cartão.

## 8. Limites conhecidos

**Afirmação.** O conhecimento vem de uma base simulada, não de dados oficiais atualizados. O agente pode produzir respostas incompletas, aceitar uma premissa incorreta ou falhar mesmo em consultas simples: a avaliação contém falhas, um erro na versão A e casos inconclusivos. A instrução “não inventar” só aparece como prompt, sem verificador final obrigatório (**LACUNA L03**). O teto de passos pode terminar sem resposta textual utilizável; falta teste específico (**LACUNA L05**). Não utilizar o agente para tomada de decisão financeira, jurídica, comercial ou de segurança veicular.

**Evidências:** [`dados/veiculos.json`](../dados/veiculos.json); [`src/main.py:L103-L117`](../src/main.py), [`L182-L197`](../src/main.py); [`evals/resultados/resumo.md`](../evals/resultados/resumo.md).

## 9. Riscos aceitos

**Estado.** Para fins de demonstração acadêmica, são **propostas de aceitação condicionada**, não decisões formalmente aprovadas: (a) imprecisão da base simulada, mitigada pelo aviso de não substituição a fontes oficiais; (b) variação nas respostas do modelo, avaliada pela suíte com repetição; (c) risco de exposição de texto livre no histórico e no provedor, **não aceitável com dados pessoais reais sem controles adicionais**. **LACUNA L18:** falta ata/registro de aceite, aprovador, data, medidas obrigatórias e condições de revogação.

**Evidências de contexto:** [`README.md`](../README.md), seções 3 e 13; [`evals/resultados/resumo.md`](../evals/resultados/resumo.md); [`src/tools.py:L39-L54`](../src/tools.py).

## 10. Supervisão humana

**Afirmação.** O modo atual é execução local iniciada pelo operador; não existe fila de autorização antes de resposta, nem revisão humana obrigatória automatizada. Os resultados `revisar` da suíte dependem de análise posterior. **LACUNA L08:** especificar se/que classes devem aguardar aprovação, o aprovador e o prazo/SLA. **LACUNA L10:** documentar quem pode suspender o agente e um procedimento comprovado de parada, revogação de chave e reativação. Até isso existir, somente testes supervisionados com dados sintéticos são recomendados.

**Evidências:** [`src/main.py:L200-L205`](../src/main.py); [`evals/executar_suite.py:L27-L71`](../evals/executar_suite.py); [`evals/resultados/resumo.md`](../evals/resultados/resumo.md), pendências.

## 11. Registro e retenção

**Afirmação.** Em uso normal, cada interação grava `pergunta`, `resposta` e `ferramenta_utilizada` no arquivo `logs/historico.jsonl`. **Não grava**, nessa função, identificador de execução, timestamp, versão do modelo, versão da base, prompt efetivo, sequência completa de ferramentas nem contexto enviado. Em avaliações, a suíte salva rastros detalhados, incluindo chamadas, resultados, duração e um carimbo com hashes da base/dataset; o ambiente de testes substitui o registrador normal em memória. **LACUNA L19:** criar trilha de auditoria completa para uso normal e teste de recuperação de uma decisão específica. **LACUNA L16:** definir prazo de retenção, descarte, controle de acesso e política de proteção de histórico/testes. A presença de um arquivo de log no repositório público também exige revisão para evitar exposição acidental.

**Evidências:** [`src/tools.py:L39-L59`](../src/tools.py); [`evals/executar_suite.py:L84-L138`](../evals/executar_suite.py), [`L189-L212`](../evals/executar_suite.py); [`.gitignore`](../.gitignore) (não ignora `logs/`).

## 12. Histórico de mudanças

| Versão / data | Mudança demonstrada | Aprovação |
|---|---|---|
| Protótipo inicial (data de release não fixada) | Consulta de veículos, listagem de versões e histórico local | **LACUNA L20:** aprovação formal e tag/commit de release |
| Suíte de avaliação v1.0.0, execução 09/10/2026 | Dataset de 20 casos; versões experimentais A e B; relatório de 80 execuções | Comparação experimental; **não comprova aprovação de promoção** (**LACUNA L20**) |
| Model card v1.0, 16/10/2026 | Inventário de evidências, autoridade, dados e lacunas | Elaborado para entrega acadêmica; **LACUNA L20:** revisão/aceite de responsável |

**Evidências:** [`evals/golden_dataset_v1.0.0.json`](../evals/golden_dataset_v1.0.0.json); [`evals/resultados/resumo.md`](../evals/resultados/resumo.md); histórico de commits do repositório: https://github.com/chequerdev/luxcar-agentes-llm/commits/main.

## Lacunas consolidadas e plano de correção

| ID | O que falta comprovar / corrigir | Prioridade |
|---|---|---|
| L01 | Registrar SHA do commit examinado e usar links permanentes por versão | Média |
| L02 | Designar responsável formal por incidentes, suplente e aprovador | Alta |
| L03 | Implementar validador fora do prompt para escopo, respostas e fatos sem fonte; testar desvios | Alta |
| L04 | Comprovar permissão somente leitura na base em ambiente de execução | Média |
| L05 | Testar exaustão dos cinco passos e garantir resposta segura em caso de limite | Alta |
| L06 | Auditar permissões, rotação, escopo e revogação da chave Groq | Alta |
| L07 | Configurar e registrar limite de gasto/uso no provedor, com evidência | Alta |
| L08 | Definir limiar de revisão/ aprovação humana, aprovador e SLA | Alta |
| L09 | Testar erros, indisponibilidade do provedor e comportamento de falha segura | Alta |
| L10 | Registrar operador autorizado e procedimento testado de suspensão/retomada | Alta |
| L11 | Revalidar inventário de MCP, RAG e novas integrações em cada release | Média |
| L12 | Fixar versão/snapshot datado do modelo ou declarar limitação de versionamento do provedor | Média |
| L13 | Confirmar documentalmente região, transferência, retenção e treino no plano Groq em uso | Alta |
| L14 | Definir hipótese legal LGPD art. 7º, aviso e regras de compartilhamento; não usar dados pessoais reais antes disso | Alta |
| L15 | Revisar a base e impedir inclusão indevida de dados identificáveis | Média |
| L16 | Implementar minimização, mascaramento, prazo de retenção, exclusão e controle de acesso a logs | Alta |
| L17 | Revisar resultados inconclusivos e medir concordância juiz/humano em 30 rótulos reais | Alta |
| L18 | Registrar aceitação de riscos, aprovador, justificativa, prazo e mitigação | Alta |
| L19 | Ampliar rastreabilidade da decisão normal: ID, hora, versões, contexto e sequência de ferramentas | Alta |
| L20 | Criar changelog com SHA/tag, data, autor e aprovação por release | Média |

## Resposta à questão do exercício

**Um auditor externo consegue decidir se uma decisão concreta estava dentro da autoridade do agente?** **Parcialmente.** Ele consegue conferir o escopo das ferramentas, a leitura da base, a escrita do histórico e o limite de passos diretamente no código. Também consegue examinar a avaliação publicada. **Ainda não consegue reconstruir com segurança toda decisão de uma execução normal**, porque o registro não vincula versões, trajetória completa, horário, contexto e aprovação humana. Para responder “sim” sem ressalvas, é necessário corrigir principalmente L01, L03, L08, L16 e L19.

### Procedimento reproduzível de conferência

Na raiz do repositório, sem publicar chaves nem entradas pessoais:

```powershell
# Identificar o commit atual
 git rev-parse HEAD
# Conferir arquivos citados
 git ls-files src/main.py src/tools.py dados/veiculos.json evals/executar_suite.py evals/resultados/resumo.md
# Conferir a existência do carimbo da execução anterior
 Get-Content evals/resultados/resumo.md
# Rodar um teste de fumaça somente após configurar GROQ_API_KEY localmente
 python evals/executar_suite.py --smoke
```

**Nota:** os comandos são instruções de verificação para o auditor, não uma saída executada e validada nesta elaboração. Não comitar `.env`, tokens, perguntas reais, CPFs ou outras informações pessoais.
