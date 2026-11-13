from evals.metricas import summarize


def test_groq_cost_from_trace_and_missing_usage():
    root = {"trace_id": "r", "inicio_ns": 0, "fim_ns": 1000, "atributos": {
        "gen_ai.operation.name": "invoke_agent", "luxcar.versao": "test",
        "luxcar.motivo_termino": "completed"}}
    chat = {"trace_id": "r", "atributos": {
        "gen_ai.operation.name": "chat", "gen_ai.provider.name": "groq",
        "gen_ai.request.model": "openai/gpt-oss-20b", "gen_ai.usage.input_tokens": 1000,
        "gen_ai.usage.output_tokens": 150}}
    assert next(summarize([root]))["custo_api_usd_por_execucao"] == 0
    assert next(summarize([root, chat]))["custo_api_usd_por_execucao"] == 0.00012
    del chat["atributos"]["gen_ai.usage.output_tokens"]
    assert next(summarize([root, chat]))["custo_api_usd_por_execucao"] is None
