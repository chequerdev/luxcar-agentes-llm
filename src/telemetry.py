"""Spans GenAI exportados em JSONL local, sem mensagens brutas ao provedor."""
from contextlib import contextmanager
from functools import wraps
import json
import os
from pathlib import Path
import re
import threading

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.sampling import ALWAYS_ON
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, SpanExporter, SpanExportResult

_lock = threading.Lock()


def safe(text):
    return re.sub(r"\b(?:\d[. ()+-]*){8,}\b", "[identificador omitido]", str(text))[:512]


def compact(obj):
    return json.dumps(obj, ensure_ascii=False, default=str, separators=(",", ":"))


class JsonlExporter(SpanExporter):
    def export(self, spans):
        path = os.getenv("LUXCAR_TRACE_FILE")
        if not path:
            return SpanExportResult.SUCCESS
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with _lock, os.fdopen(os.open(p, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600), "a", encoding="utf-8") as out:
            for span in spans:
                ctx = span.context
                out.write(compact({"nome": span.name, "trace_id": f"{ctx.trace_id:032x}",
                                   "span_id": f"{ctx.span_id:016x}",
                                   "pai": f"{span.parent.span_id:016x}" if span.parent else None,
                                   "inicio_ns": span.start_time, "fim_ns": span.end_time,
                                   "status": span.status.status_code.name,
                                   "atributos": dict(span.attributes or {}),
                                   "eventos": [{"nome": e.name, "tempo_ns": e.timestamp, "atributos": dict(e.attributes or {})}
                                               for e in span.events if e.name != "exception"]}) + "\n")
        return SpanExportResult.SUCCESS


provider = TracerProvider(shutdown_on_exit=False, sampler=ALWAYS_ON)
provider.add_span_processor(SimpleSpanProcessor(JsonlExporter()))
tracer = provider.get_tracer("luxcar.genai")


@contextmanager
def tool(name, args):
    with tracer.start_as_current_span(f"execute_tool {name}", record_exception=False,
                                      attributes={"gen_ai.operation.name": "execute_tool",
                                                  "gen_ai.tool.name": name,
                                                  "gen_ai.tool.call.arguments": compact(args)}) as span:
        yield span


def agent_span(operation):
    def decorator(fn):
        @wraps(fn)
        def wrapper(first, *args, **kwargs):
            if operation == "iniciar":
                text = first if isinstance(first, str) else first.text
            else:
                text = "Retomada de revisão"
            with tracer.start_as_current_span("invoke_agent luxcar", record_exception=False, attributes={
                "gen_ai.operation.name": "invoke_agent", "gen_ai.agent.name": "luxcar",
                "luxcar.versao": "3.0.1", "luxcar.fase": operation, "luxcar.entrada": safe(text),
            }) as span:
                from .config import MODEL, PROVIDER
                from .prompt_loader import prompt_versions
                span.set_attributes({"gen_ai.request.model": MODEL, "gen_ai.provider.name": PROVIDER,
                                     "luxcar.prompts": compact(prompt_versions())})
                try:
                    output = fn(first, *args, **kwargs)
                except Exception:
                    span.set_attribute("luxcar.motivo_termino", "erro")
                    raise
                span.set_attributes({"luxcar.motivo_termino": output.termination_reason,
                                     "luxcar.status": output.status, "luxcar.saida": safe(output.result),
                                     "luxcar.thread_id": output.thread_id,
                                     "luxcar.contexto_ids": tuple(s.source_id for s in output.sources)})
                return output
        return wrapper
    return decorator
