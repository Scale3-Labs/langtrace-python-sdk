import json
from typing import Any, Callable, List

from agents.exceptions import (InputGuardrailTripwireTriggered,
                               OutputGuardrailTripwireTriggered)
from agents.run import Runner
from importlib_metadata import version as v
from langtrace.trace_attributes import FrameworkSpanAttributes, SpanAttributes
from opentelemetry import baggage, trace
from opentelemetry.trace import SpanKind, Tracer
from opentelemetry.trace.status import Status, StatusCode

from langtrace_python_sdk.constants import LANGTRACE_SDK_NAME
from langtrace_python_sdk.constants.instrumentation.common import (
    LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY, SERVICE_PROVIDERS)
from langtrace_python_sdk.utils.llm import (set_event_completion,
                                            set_span_attributes,
                                            set_usage_attributes)


def extract_agent_details(agent_or_handoff):
    """Extract relevant details from an agent/handoff and its handoffs."""
    try:
        if agent_or_handoff is None:
            return None

        # Handle both Agent and Handoff types
        if hasattr(agent_or_handoff, 'agent'):  # This is a Handoff
            agent = agent_or_handoff.agent
        else:  # This is an Agent
            agent = agent_or_handoff

        if agent is None:
            return None

        agent_details = {
            "name": getattr(agent, 'name', None),
            "instructions": getattr(agent, 'instructions', None),
            "handoff_description": getattr(agent, 'handoff_description', None),
            "handoffs": []
        }

        if hasattr(agent, 'handoffs') and agent.handoffs:
            for handoff_item in agent.handoffs:
                handoff_details = extract_agent_details(handoff_item)
                if handoff_details:
                    agent_details["handoffs"].append(handoff_details)

        return agent_details
    except Exception:  # Catch all exceptions and fail silently
        return None


def extract_handoff_details(handoff):
    """Extract relevant details from a Handoff object."""
    try:
        if handoff is None:
            return None

        return {
            "tool_name": getattr(handoff, 'tool_name', None),
            "tool_description": getattr(handoff, 'tool_description', None),
            "agent_name": getattr(handoff, 'agent_name', None),
            "input_json_schema": getattr(handoff, 'input_json_schema', {}),
            "strict_json_schema": getattr(handoff, 'strict_json_schema', False)
        }
    except Exception:  # Catch all exceptions and fail silently
        return None


def get_handoffs(version: str, tracer: Tracer) -> Callable:
    """Wrap the `prompt` method of the `TLM` class to trace it."""

    def traced_method(
        wrapped: Callable,
        instance: Any,
        args: List[Any],
        kwargs: Any,
    ) -> Any:
        try:
            service_provider = SERVICE_PROVIDERS["OPENAI"]
            extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)
            span_attributes = {
                "langtrace.sdk.name": "langtrace-python-sdk",
                "langtrace.service.name": service_provider,
                "langtrace.service.type": "framework",
                "langtrace.service.version": version,
                "langtrace.version": v(LANGTRACE_SDK_NAME),
                **(extra_attributes if extra_attributes is not None else {}),
            }

            # Process agents from args
            agents_list = []
            if args:
                for arg in args:
                    try:
                        if arg is not None:
                            if hasattr(arg, 'name') or hasattr(arg, 'agent'):
                                agent_details = extract_agent_details(arg)
                                if agent_details:
                                    agents_list.append(agent_details)
                            elif isinstance(arg, (list, tuple)):
                                for item in arg:
                                    if item is not None and (hasattr(item, 'name') or hasattr(item, 'agent')):
                                        agent_details = extract_agent_details(item)
                                        if agent_details:
                                            agents_list.append(agent_details)
                    except Exception:
                        continue  # Skip any errors in processing individual arguments

            if agents_list:
                try:
                    span_attributes["openai_agents.agents"] = json.dumps(agents_list)
                except Exception:
                    pass  # Silently fail if JSON serialization fails

            attributes = FrameworkSpanAttributes(**span_attributes)

            with tracer.start_as_current_span(
                name=f"openai_agents.available_handoffs", kind=SpanKind.CLIENT
            ) as span:
                try:
                    set_span_attributes(span, attributes)
                    result = wrapped(*args, **kwargs)
                    
                    # Process handoff results
                    if result is not None:
                        handoffs_list = []
                        try:
                            if isinstance(result, (list, tuple)):
                                for handoff in result:
                                    if handoff is not None and hasattr(handoff, 'tool_name'):
                                        handoff_details = extract_handoff_details(handoff)
                                        if handoff_details:
                                            handoffs_list.append(handoff_details)
                            elif hasattr(result, 'tool_name'):
                                handoff_details = extract_handoff_details(result)
                                if handoff_details:
                                    handoffs_list.append(handoff_details)

                            if handoffs_list:
                                try:
                                    span.set_attribute("openai_agents.handoffs", json.dumps(handoffs_list))
                                    span.set_status(Status(StatusCode.OK))
                                except Exception:
                                    pass  # Silently fail if JSON serialization fails
                        except Exception:
                            pass  # Silently fail if handoff processing fails

                    return result

                except Exception as err:
                    try:
                        span.record_exception(err)
                        span.set_status(Status(StatusCode.ERROR, str(err)))
                    except Exception:
                        pass  # Silently fail if error recording fails
                    raise  # Re-raise the original error since it's from the wrapped function

        except Exception as outer_err:
            # If anything fails in our instrumentation wrapper, catch it and return control to the wrapped function
            try:
                return wrapped(*args, **kwargs)
            except Exception as wrapped_err:
                raise wrapped_err  # Only raise errors from the wrapped function

    return traced_method


def extract_response_input_details(input_item):
    """Extract relevant details from a response input item."""
    try:
        if input_item is None:
            return None

        details = {
            "type": input_item.__class__.__name__,
        }

        # Extract common attributes that might be present
        for attr in ['content', 'role', 'name', 'tool_name', 'tool_call_id']:
            if hasattr(input_item, attr):
                value = getattr(input_item, attr)
                if value is not None:
                    details[attr] = value

        return details
    except Exception:
        return None


def extract_model_response(response):
    """Extract relevant details from a ModelResponse."""
    try:
        if response is None:
            return None

        response_dict = {
            "referenceable_id": getattr(response, "referenceable_id", None),
            "usage": {
                "requests": getattr(response.usage, "requests", 0),
                "input_tokens": getattr(response.usage, "input_tokens", 0),
                "output_tokens": getattr(response.usage, "output_tokens", 0),
                "total_tokens": getattr(response.usage, "total_tokens", 0)
            },
            "output": []
        }

        # Extract output messages or function calls
        if response.output:
            for output_item in response.output:
                if hasattr(output_item, 'type'):
                    if output_item.type == 'function_call':
                        # Handle function call
                        function_call = {
                            "id": getattr(output_item, "id", None),
                            "type": "function_call",
                            "status": getattr(output_item, "status", None),
                            "call_id": getattr(output_item, "call_id", None),
                            "name": getattr(output_item, "name", None),
                            "arguments": getattr(output_item, "arguments", "{}")
                        }
                        response_dict["output"].append(function_call)
                        # Set response type as function_call and capture the function name
                        response_dict["response_type"] = "function_call"
                        response_dict["function"] = getattr(output_item, "name", None)
                    elif output_item.type == 'message':
                        # Handle regular message
                        message = {
                            "id": getattr(output_item, "id", None),
                            "role": getattr(output_item, "role", None),
                            "status": getattr(output_item, "status", None),
                            "type": "message",
                            "content": []
                        }
                        
                        # Extract content (text, annotations, etc.)
                        if hasattr(output_item, 'content') and output_item.content:
                            for content_item in output_item.content:
                                content_dict = {
                                    "type": getattr(content_item, "type", None),
                                    "text": getattr(content_item, "text", None),
                                    "annotations": getattr(content_item, "annotations", [])
                                }
                                message["content"].append(content_dict)
                        
                        response_dict["output"].append(message)
                        # Set response type as response for messages
                        if "response_type" not in response_dict:
                            response_dict["response_type"] = "response"

        return response_dict
    except Exception:
        return None


def extract_message_history(messages):
    """Extract relevant details from message history."""
    try:
        if not messages or not isinstance(messages, list):
            return []

        history = []
        for msg in messages:
            if not isinstance(msg, dict):
                continue

            message = {}
            # Extract common fields
            for key in ['content', 'role', 'id', 'type', 'status']:
                if key in msg:
                    message[key] = msg[key]

            # Extract function call specific fields
            if msg.get('type') == 'function_call':
                for key in ['arguments', 'call_id', 'name']:
                    if key in msg:
                        message[key] = msg[key]

            # Extract function output
            if msg.get('type') == 'function_call_output':
                for key in ['call_id', 'output']:
                    if key in msg:
                        message[key] = msg[key]

            if message:
                history.append(message)

        return history
    except Exception:
        return []


def extract_run_context(context):
    """Extract relevant details from RunContextWrapper."""
    try:
        if context is None:
            return None

        return {
            "usage": {
                "requests": getattr(context.usage, "requests", 0),
                "input_tokens": getattr(context.usage, "input_tokens", 0),
                "output_tokens": getattr(context.usage, "output_tokens", 0),
                "total_tokens": getattr(context.usage, "total_tokens", 0)
            }
        }
    except Exception:
        return None


def extract_run_config(config):
    """Extract relevant details from RunConfig."""
    try:
        if config is None:
            return None

        return {
            "workflow_name": getattr(config, "workflow_name", None),
            "trace_id": getattr(config, "trace_id", None),
            "group_id": getattr(config, "group_id", None),
            "tracing_disabled": getattr(config, "tracing_disabled", False),
            "trace_include_sensitive_data": getattr(config, "trace_include_sensitive_data", True)
        }
    except Exception:
        return None


def get_new_response(version: str, tracer: Tracer) -> Callable:
    """Wrap the _get_new_response method to trace inputs and outputs."""

    async def traced_method(
        wrapped: Callable,
        instance: Any,
        args: List[Any],
        kwargs: Any,
    ) -> Any:
        try:
            service_provider = SERVICE_PROVIDERS["OPENAI"]
            extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)
            span_attributes = {
                "langtrace.sdk.name": "langtrace-python-sdk",
                "langtrace.service.name": service_provider,
                "langtrace.service.type": "framework",
                "langtrace.service.version": version,
                "langtrace.version": v(LANGTRACE_SDK_NAME),
                **(extra_attributes if extra_attributes is not None else {}),
            }

            # Process input arguments
            try:
                if args and len(args) >= 7:  # Check if we have all expected arguments
                    agent = args[0]
                    agent_name = getattr(agent, 'name', None) if agent else None
                    input_details = {
                        "agent": extract_agent_details(agent),
                        "instructions": args[1],
                        "message_history": extract_message_history(args[2]),
                        "run_context": extract_run_context(args[5]),
                        "run_config": extract_run_config(args[6])
                    }
                    span_attributes["openai_agents.inputs"] = json.dumps(input_details)

                    # Set standard LLM prompts attribute
                    if args[2]:  # message_history exists
                        messages = []
                        for msg in args[2]:
                            if isinstance(msg, dict):
                                messages.append({
                                    "role": msg.get("role", "user"),
                                    "content": msg.get("content", "")
                                })
                        if messages:
                            span_attributes[SpanAttributes.LLM_PROMPTS] = json.dumps(messages)
            except Exception:
                pass  # Silently fail if input processing fails

            attributes = FrameworkSpanAttributes(**span_attributes)
            # Determine span name based on agent name
            agent_name = getattr(args[0], 'name', None) if args and len(args) > 0 else None
            span_name = (f"openai_agents.{agent_name}" if agent_name
                         else "openai_agents.agent_response")

            with tracer.start_as_current_span(
                name=span_name,
                kind=SpanKind.CLIENT
            ) as span:
                try:
                    set_span_attributes(span, attributes)

                    # Get the model from _get_model
                    agent = args[0] if args and len(args) > 0 else None
                    run_config = args[6] if args and len(args) > 6 else None
                    if agent and run_config:
                        try:
                            model = Runner._get_model(agent, run_config)
                            if hasattr(model, 'model'):
                                model_name = None
                                if isinstance(model.model, str):
                                    model_name = model.model
                                elif hasattr(model.model, 'model_name'):
                                    model_name = model.model.model_name
                                if model_name:
                                    span.set_attribute(SpanAttributes.LLM_REQUEST_MODEL, model_name)
                        except Exception:
                            pass  # Silently fail if model extraction fails

                    result = await wrapped(*args, **kwargs)

                    # Process response output
                    if result is not None:
                        try:
                            response_dict = extract_model_response(result)
                            if response_dict:
                                # Set the main response output
                                span.set_attribute("openai_agents.outputs", json.dumps(response_dict))

                                # Set response type and function details as separate attributes for easier querying
                                span.set_attribute("openai_agents.response_type", response_dict.get("response_type", "response"))
                                if response_dict.get("response_type") == "function_call" and "function" in response_dict:
                                    span.set_attribute("openai_agents.function", response_dict["function"])

                                # Set usage attributes using the llm utility function
                                if "usage" in response_dict:
                                    set_usage_attributes(span, response_dict["usage"])

                                # Set standard LLM completion event
                                if "output" in response_dict:
                                    completions = []
                                    for output in response_dict["output"]:
                                        if output["type"] == "message":
                                            content = " ".join([item.get("text", "") for item in output.get("content", [])])
                                            completions.append({
                                                "role": output.get("role", "assistant"),
                                                "content": content
                                            })
                                        elif output["type"] == "function_call":
                                            completions.append({
                                                "role": "assistant",
                                                "function_call": {
                                                    "name": output.get("name"),
                                                    "arguments": output.get("arguments", "{}")
                                                }
                                            })
                                    if completions:
                                        set_event_completion(span, completions)

                                span.set_status(Status(StatusCode.OK))
                        except Exception:
                            pass  # Silently fail if response processing fails

                    return result

                except InputGuardrailTripwireTriggered as err:
                    # Handle guardrail tripwire specifically
                    guardrail_name = err.guardrail_result.guardrail.__class__.__name__
                    error_msg = f"Input guardrail {guardrail_name} triggered tripwire"

                    # Set error attributes and status on current span
                    span.set_attribute("error.type", "input_guardrail_tripwire")
                    span.set_attribute("error.guardrail", guardrail_name)
                    span.record_exception(err)
                    span.set_status(Status(StatusCode.ERROR, error_msg))

                    # Get the current context and root span
                    ctx = trace.get_current_span().get_span_context()
                    if ctx:
                        root_span = trace.get_tracer(__name__).start_span(
                            "root_span",
                            context=ctx,
                            kind=SpanKind.CLIENT
                        )
                        root_span.set_attribute("error.type", "input_guardrail_tripwire")
                        root_span.set_attribute("error.guardrail", guardrail_name)
                        root_span.record_exception(err)
                        root_span.set_status(Status(StatusCode.ERROR, error_msg))
                        root_span.end()

                    raise
                except OutputGuardrailTripwireTriggered as err:
                    # Handle guardrail tripwire specifically
                    guardrail_name = err.guardrail_result.guardrail.__class__.__name__
                    error_msg = f"Output guardrail {guardrail_name} triggered tripwire"

                    # Set error attributes and status on current span
                    span.set_attribute("error.type", "output_guardrail_tripwire")
                    span.set_attribute("error.guardrail", guardrail_name)
                    span.record_exception(err)
                    span.set_status(Status(StatusCode.ERROR, error_msg))

                    # Get the current context and root span
                    ctx = trace.get_current_span().get_span_context()
                    if ctx:
                        root_span = trace.get_tracer(__name__).start_span(
                            "root_span",
                            context=ctx,
                            kind=SpanKind.CLIENT
                        )
                        root_span.set_attribute("error.type", "output_guardrail_tripwire")
                        root_span.set_attribute("error.guardrail", guardrail_name)
                        root_span.record_exception(err)
                        root_span.set_status(Status(StatusCode.ERROR, error_msg))
                        root_span.end()

                    raise
                except Exception as err:
                    error_msg = str(err)

                    # Set error status on current span
                    span.record_exception(err)
                    span.set_status(Status(StatusCode.ERROR, error_msg))

                    # Get the current context and root span
                    ctx = trace.get_current_span().get_span_context()
                    if ctx:
                        root_span = trace.get_tracer(__name__).start_span(
                            "root_span",
                            context=ctx,
                            kind=SpanKind.CLIENT
                        )
                        root_span.record_exception(err)
                        root_span.set_status(Status(StatusCode.ERROR, error_msg))
                        root_span.end()

                    raise

        except Exception as outer_err:
            try:
                return await wrapped(*args, **kwargs)
            except Exception as wrapped_err:
                raise wrapped_err

    return traced_method
