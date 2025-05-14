import base64
from langtrace_python_sdk.utils.llm import (
    get_langtrace_attributes,
    get_llm_request_attributes,
    set_span_attributes,
    set_usage_attributes,
    set_span_attribute,
    set_event_completion,
)
from langtrace_python_sdk.utils import handle_span_error

from opentelemetry.trace import Tracer, SpanKind
from opentelemetry.sdk.trace import Span
from langtrace.trace_attributes import SpanAttributes

from typing import Iterator

def capture_input_data(contents):
    input_data = []
    
    if isinstance(contents, list):
        content_parts = []
        for content in contents:
            if hasattr(content, 'parts'):
                for part in content.parts:
                    if hasattr(part, 'text') and part.text:
                        content_parts.append({
                            "type": "text",
                            "text": part.text
                        })
                    if hasattr(part, 'inline_data') and part.inline_data:
                        content_parts.append({
                            "type": "image_url",
                            "image_url": f"data:{part.inline_data.mime_type};base64,{base64.b64encode(part.inline_data.data).decode('utf-8')}"
                        })
            else:
                if isinstance(content, str):
                    content_parts.append({
                        "type": "text",
                        "text": content
                    })
                elif hasattr(content, 'text') and content.text:
                    content_parts.append({
                        "type": "text",
                        "text": content.text
                    })
                elif hasattr(content, 'inline_data') and content.inline_data:
                    content_parts.append({
                        "type": "image_url",
                        "image_url": f"data:{content.inline_data.mime_type};base64,{base64.b64encode(content.inline_data.data).decode('utf-8')}"
                    })
                else:
                    content_parts.append({
                        "type": "text",
                        "text": content
                    })
        input_data.append({
            "role": "user",
            "content": content_parts
        })
    else:
        input_data.append({
            "role": "user",
            "content": contents
        })
    
    return input_data


def patch_google_genai(tracer: Tracer, version: str):
    def traced_method(wrapped, instance, args, kwargs):
        span_attributes = {
            **get_langtrace_attributes(
                service_provider="google_genai", version=version
            ),
            **get_llm_request_attributes(kwargs=kwargs, prompts=capture_input_data(kwargs["contents"])),
        }
        with tracer.start_as_current_span(
            name="google.genai.generate_content",
            kind=SpanKind.CLIENT,
        ) as span:
            try:
                set_span_attributes(span, span_attributes)
                response = wrapped(*args, **kwargs)
                set_response_attributes(span, response)
                return response
            except Exception as error:
                handle_span_error(span, error)
                raise

    return traced_method


def patch_google_genai_streaming(tracer: Tracer, version: str):
    def traced_method(wrapped, instance, args, kwargs):
        prompt = [
            {
                "role": "user",
                "content": kwargs["contents"],
            }
        ]
        span_attributes = {
            **get_langtrace_attributes(
                service_provider="google_genai", version=version
            ),
            **get_llm_request_attributes(kwargs=kwargs, prompts=prompt),
        }
        with tracer.start_as_current_span(
            name="google.genai.generate_content_stream",
            kind=SpanKind.CLIENT,
        ) as span:
            set_span_attributes(span, span_attributes)
            response = wrapped(*args, **kwargs)
            set_streaming_response_attributes(span, response)
            return response

    return traced_method


def set_streaming_response_attributes(span: Span, response):
    accum_completion = ""
    for chunk in response:
        set_span_attribute(
            span,
            SpanAttributes.LLM_RESPONSE_MODEL,
            chunk.model_version,
        )
        candidates = chunk.candidates
        for candidate in candidates:
            set_span_attribute(
                span,
                SpanAttributes.LLM_RESPONSE_FINISH_REASON,
                candidate.finish_reason,
            )

            accum_completion += candidate.content.parts[0].text

        if chunk.usage_metadata:
            set_usage_attributes(
                span,
                {
                    "input_tokens": chunk.usage_metadata.prompt_token_count,
                    "output_tokens": chunk.usage_metadata.candidates_token_count,
                },
            )
    set_event_completion(span, [{"role": "assistant", "content": accum_completion}])


def set_response_attributes(span: Span, response):
    completions = []
    for candidate in response.candidates:
        set_span_attribute(
            span, SpanAttributes.LLM_RESPONSE_FINISH_REASON, candidate.finish_reason
        )
        parts = candidate.content.parts
        role = candidate.content.role
        completion = {
            "role": role or "assistant",
            "content": [part.text for part in parts],
        }
        completions.append(completion)

    set_span_attribute(span, SpanAttributes.LLM_RESPONSE_MODEL, response.model_version)
    set_event_completion(span, completions)
    if response.usage_metadata:
        set_usage_attributes(
            span,
            {
                "input_tokens": response.usage_metadata.prompt_token_count,
                "output_tokens": response.usage_metadata.candidates_token_count,
            },
        )
