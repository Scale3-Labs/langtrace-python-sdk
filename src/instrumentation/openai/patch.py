import json
from opentelemetry import trace
from opentelemetry.trace import Span, SpanKind, StatusCode
from instrumentation.openai.lib.apis import APIS
from instrumentation.openai.lib.span_attributes import OpenAISpanAttributes
from constants import SERVICE_PROVIDERS, TRACE_NAMESPACES
from opentelemetry import trace
from opentelemetry.trace import SpanKind, StatusCode


def chat_completion_create():

    tracer = trace.get_tracer(TRACE_NAMESPACES['OPENAI'])
    service_provider = SERVICE_PROVIDERS['OPENAI']
    attributes = {
      "service.provider": service_provider,      
    }
    # Set attributes to the span
    for key, value in attributes.items():
        span.set_attribute(key, value)
    span = tracer.start_span("span_name")
    span.set_attribute("user_id", "123")
    # Set status of the span to OK
    span.set_attribute("status_code", "OK")

    # span.set_attribute("request.prompts", prompts_json)
    span.set_attribute("status_code", "OK")
    span.set_attribute("temperature", "0")
    # End the span
    span.end()
    
    
