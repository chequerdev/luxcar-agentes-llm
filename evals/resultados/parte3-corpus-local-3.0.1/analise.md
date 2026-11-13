# Recuperação documental | execução local 3.0.1

Pergunta: “Qual é a política de privacidade do LuxCar sobre CPF, placa e identidade do proprietário?”

A raiz do [trace](traces.jsonl) registrou a versão 3.0.1, status
answered e término completed. O span filho execute_tool
buscar_corpus_textual registrou top_k=3 e os três trechos retornados.
A primeira fonte da [saída](saida.json) é politicas-v2#s4, a seção vigente
de privacidade. Nenhum dado pessoal real foi incluído no pedido e
nenhuma ação de escrita foi solicitada.

Esta é uma demonstração do caminho documental no modo local. Não houve
chamada ao provedor nem inclusão nos denominadores das rodadas principais.

Para repetir no PowerShell a partir da raiz do projeto:

    $env:LUXCAR_USE_LLM = "0"
    $env:LUXCAR_TRACE_FILE = ".runtime\trace-corpus.jsonl"
    .\.venv\Scripts\python.exe -m src.main "Qual é a política de privacidade do LuxCar sobre CPF, placa e identidade do proprietário?" --user-id demo-corpus --session-id demonstracao --case-id corpus-01
