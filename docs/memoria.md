# Memória implementada

## Dois níveis e três estruturas

| | Curto prazo | Longo prazo |
|---|---|---|
| Conteúdo | entrada, decisão, trajetória, fontes, ação e aprovação | episódios, fatos semânticos e regra procedural |
| Persistência | checkpoint SQLite | tabelas SQLite + prompts versionados |
| Leitura | retomada por `thread_id` | chave ou similaridade a cada execução |
| Ciclo | conversa/ação pendente | atravessa execuções até remoção |

| Estrutura | Escopo e função no LuxCar |
|---|---|
| checkpoint | estado íntegro de uma conversa para retomar `interrupt`, sem repetir escrita |
| memória | fragmentos selecionados: episódios e fatos do usuário |
| RAG | documentos/veículos externos ao histórico; o agente não os escreve |

Serializar tudo não substitui memória: a recuperação por relevância traz episódios relacionados e deixa para trás trajetória, payloads e eventos irrelevantes.

## Três memórias

- episódica: resumos de consultas em `episodic_memory`, recuperados por similaridade Jaccard de tokens;
- semântica: chave-valor por usuário em `semantic_memory`; timestamp mais novo vence contradição;
- procedural: regras em `src/prompts/answer-v2.md`, sob versionamento Git.

Política de escrita: código registra no máximo um episódio por resposta suficiente; fatos semânticos só entram por chamadas explícitas permitidas. Cada conteúdo recebe SHA-256; a resposta inclui `ja_existia`.

## Esquecimento

- contradição: não apaga histórico; leitura semântica usa a versão mais nova da chave;
- remoção: `forget_user_everywhere` remove `semantic_memory`, `episodic_memory`, `actions`, todas as tabelas de checkpoint com `thread_id`, redige o identificador em logs JSON/JSONL e falha se o identificador tiver contaminado um prompt procedural.

Não há decaimento automático: corpus pequeno e taxa de mudança desconhecida não justificam corte arbitrário. A remoção completa é executada por `python -m scripts.remover_usuario --user-id ID`; logs entregues usam dados fictícios.

## Conversa

`thread_id = user_id:session_id:case_id`. Duas conversas simultâneas usam `session_id` diferentes. O checkpoint `.runtime/checkpoints.sqlite` sobrevive ao processo, mas não é replicado.

Ordem de descarte planejada se a janela crescer: (1) retornos de ferramenta já usados, (2) episódios menos similares, (3) mensagens antigas sumarizadas. Nunca descartar system prompt, solicitação atual, ação pendente nem última decisão humana. Hoje não há histórico textual longo no estado, então não ocorre truncamento silencioso.

Da conversa para longo prazo sobrevivem apenas episódios de consulta suficiente e fatos permitidos; prompts, corpus e checkpoint não são copiados.
