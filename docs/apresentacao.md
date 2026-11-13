# Roteiro de apresentação | LuxCar

Duração sugerida: 7 a 9 minutos. Gabriel apresenta os slides 1 a 4.
Anderson apresenta os slides 5 a 8 e conduz a demonstração. Troquem a
divisão se for mais confortável.

- **1 a 2 | 1 min.** O LuxCar consulta especificações e políticas e registra
  interesse mediante revisão. Nesta Parte 3 usamos o grafo da Parte 2.
- **3 a 4 | 2 min.** A mesma suíte passou de 26/30 para 30/30 em modo local.
  O juiz de clareza é outra avaliação. Concordou em 22/30, abaixo do limiar,
  e não foi adotado.
- **5 a 7 | 2 a 3 min.** Três controles fora do prompt, as métricas locais e
  uma aprovação reconstruída pelo trace. O CLI não autentica o operador.
- **8 | 2 a 3 min.** Consulta, revisão e aprovação. Se a demo falhar, use
  o trace já publicado e explicado no slide 7.

## Demo em PowerShell no Windows

Na raiz do projeto e com a venv instalada, execute uma linha por vez.
A sessão aleatória evita conflito com um ensaio anterior.

```powershell
$env:LUXCAR_USE_LLM = "0"
$env:LUXCAR_TRACE_FILE = ".runtime\trace-apresentacao.jsonl"
$sessao = "demo-" + (Get-Date -Format "yyyyMMddHHmmss")
.\.venv\Scripts\python.exe -m src.main "Qual câmbio o Polo TSI 2018 possui?" --user-id demo --session-id $sessao --case-id consulta
.\.venv\Scripts\python.exe -m src.main "Registre meu interesse no Polo TSI 2018, telefone 11999998888" --user-id demo --session-id $sessao --case-id interesse
.\.venv\Scripts\python.exe -m src.main --resume-thread "demo:${sessao}:interesse" --decision approve
Get-Content .runtime\trace-apresentacao.jsonl -Tail 3
```

Mostre primeiro `answered` com fonte `veiculo:1`. No pedido de interesse,
mostre `pending_approval`. A confirmação deve produzir `approved` e uma
chave de idempotência. Se a demo cair, abra o [model card](model-card.md),
que indica o trace original e o que aconteceu em cada etapa.

## Perguntas que podem aparecer

- **O juiz falhou?** Ele não atingiu o limiar de adoção. O ganho foi
  descobrir em que tipo de resposta ele discordava dos revisores.
- **30/30 prova que pode ir para produção?** Não. É desempenho no conjunto
  local. Os números não garantem generalização nem desempenho remoto.
- **O prompt consegue aprovar sozinho?** Não. A escrita é um caminho
  separado depois de um evento de revisão. No protótipo, a identidade do
  revisor no terminal é declarada, não autenticada.
