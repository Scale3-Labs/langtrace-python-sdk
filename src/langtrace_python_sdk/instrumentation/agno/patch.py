"""
Copyright (c) 2025 Scale3 Labs

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import json
import time
from typing import Any

from importlib_metadata import version as v
from langtrace.trace_attributes import FrameworkSpanAttributes
from opentelemetry import baggage
from opentelemetry.trace import Span, SpanKind, Tracer
from opentelemetry.trace.status import Status, StatusCode

from langtrace_python_sdk.constants import LANGTRACE_SDK_NAME
from langtrace_python_sdk.constants.instrumentation.common import (
    LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY,
    SERVICE_PROVIDERS,
)
from langtrace_python_sdk.utils import set_span_attribute
from langtrace_python_sdk.utils.llm import get_span_name, set_span_attributes
from langtrace_python_sdk.utils.misc import serialize_args, serialize_kwargs


def patch_agent(operation_name, version, tracer: Tracer):
    def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS.get("AGNO", "agno")
        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)

        span_attributes = {
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "framework",
            "langtrace.service.version": version,
            "langtrace.version": v(LANGTRACE_SDK_NAME),
            **(extra_attributes if extra_attributes is not None else {}),
        }

        inputs = {}
        if len(args) > 0:
            inputs["args"] = serialize_args(*args)
        if len(kwargs) > 0:
            inputs["kwargs"] = serialize_kwargs(**kwargs)
        span_attributes["agno.agent.inputs"] = json.dumps(inputs)
        attributes = FrameworkSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(
            get_span_name(operation_name), kind=SpanKind.CLIENT
        ) as span:
            try:
                set_span_attributes(span, attributes)
                AgnoSpanAttributes(span=span, instance=instance)
                
                result = wrapped(*args, **kwargs)
                
                span.set_status(Status(StatusCode.OK))

                if operation_name in ["Agent._run", "Agent._arun", "Agent.run", "Agent.arun", "Agent.print_response"]:
                    try:
                        if hasattr(instance, "run_response") and instance.run_response:
                            if hasattr(instance.run_response, "run_id") and instance.run_response.run_id:
                                set_span_attribute(span, "agno.agent.run_id", instance.run_response.run_id)
                            
                            if hasattr(instance.run_response, "created_at") and instance.run_response.created_at:
                                set_span_attribute(span, "agno.agent.timestamp", instance.run_response.created_at)

                            if hasattr(instance.run_response, "content") and instance.run_response.content:
                                content = str(instance.run_response.content)
                                set_span_attribute(span, "agno.agent.response_content", content)
                            
                            # Capture any tools that were used
                            if hasattr(instance.run_response, "tools") and instance.run_response.tools:
                                tools = instance.run_response.tools
                                tool_summary = []
                                for tool in tools:
                                    if 'tool_name' in tool:
                                        tool_summary.append(tool['tool_name'])
                                    elif 'function' in tool and 'name' in tool['function']:
                                        tool_summary.append(tool['function']['name'])
                                set_span_attribute(span, "agno.agent.tools_used", json.dumps(tool_summary))

                            if hasattr(instance.run_response, "metrics") and instance.run_response.metrics:
                                metrics = instance.run_response.metrics
                                for metric_name, metric_values in metrics.items():
                                    if isinstance(metric_values, list):

                                        if all(isinstance(v, (int, float)) for v in metric_values):
                                            set_span_attribute(
                                                span,
                                                f"agno.agent.metrics.{metric_name}",
                                                sum(metric_values) / len(metric_values) if metric_values else 0
                                            )
                                        elif len(metric_values) > 0:
                                            set_span_attribute(
                                                span,
                                                f"agno.agent.metrics.{metric_name}",
                                                str(metric_values[-1])
                                            )
                                    else:
                                        set_span_attribute(
                                            span,
                                            f"agno.agent.metrics.{metric_name}",
                                            str(metric_values)
                                        )

                                if 'input_tokens' in metrics:
                                    if isinstance(metrics['input_tokens'], list) and metrics['input_tokens']:
                                        set_span_attribute(span, "agno.agent.token_usage.input", 
                                                           sum(metrics['input_tokens']))
                                    else:
                                        set_span_attribute(span, "agno.agent.token_usage.input", 
                                                           metrics['input_tokens'])
                                
                                if 'output_tokens' in metrics:
                                    if isinstance(metrics['output_tokens'], list) and metrics['output_tokens']:
                                        set_span_attribute(span, "agno.agent.token_usage.output", 
                                                           sum(metrics['output_tokens']))
                                    else:
                                        set_span_attribute(span, "agno.agent.token_usage.output", 
                                                           metrics['output_tokens'])
                                
                                if 'total_tokens' in metrics:
                                    if isinstance(metrics['total_tokens'], list) and metrics['total_tokens']:
                                        set_span_attribute(span, "agno.agent.token_usage.total", 
                                                           sum(metrics['total_tokens']))
                                    else:
                                        set_span_attribute(span, "agno.agent.token_usage.total", 
                                                           metrics['total_tokens'])
                    except Exception as err:
                        set_span_attribute(span, "agno.agent.run_response_error", str(err))
                
                return result
            
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise
    
    return traced_method


def patch_memory(operation_name, version, tracer: Tracer):
    """
    Apply instrumentation patches to AgentMemory class methods.
    
    Args:
        operation_name: The name of the operation
        version: The version of Agno
        tracer: The OpenTelemetry tracer
    """
    def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS.get("AGNO", "agno")
        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)
        
        # Collect basic span attributes
        span_attributes = {
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "framework",
            "langtrace.service.version": version,
            "langtrace.version": v(LANGTRACE_SDK_NAME),
            **(extra_attributes if extra_attributes is not None else {}),
        }

        # Collect inputs
        inputs = {}
        if len(args) > 0:
            inputs["args"] = serialize_args(*args)
        if len(kwargs) > 0:
            inputs["kwargs"] = serialize_kwargs(**kwargs)
        
        span_attributes["agno.memory.inputs"] = json.dumps(inputs)

        if hasattr(instance, "messages"):
            span_attributes["agno.memory.messages_count_before"] = len(instance.messages)
        if hasattr(instance, "runs"):
            span_attributes["agno.memory.runs_count_before"] = len(instance.runs)
        if hasattr(instance, "memories") and instance.memories:
            span_attributes["agno.memory.memories_count_before"] = len(instance.memories)

        attributes = FrameworkSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(
            get_span_name(operation_name), kind=SpanKind.CLIENT
        ) as span:
            start_time = time.time()
            try:
                # Set attributes
                set_span_attributes(span, attributes)
                
                # Execute the wrapped method
                result = wrapped(*args, **kwargs)
                
                # Add memory stats after operation
                if hasattr(instance, "messages"):
                    set_span_attribute(span, "agno.memory.messages_count_after", len(instance.messages))
                if hasattr(instance, "runs"):
                    set_span_attribute(span, "agno.memory.runs_count_after", len(instance.runs))
                if hasattr(instance, "memories") and instance.memories:
                    set_span_attribute(span, "agno.memory.memories_count_after", len(instance.memories))
                
                # Record execution time
                set_span_attribute(span, "agno.memory.execution_time_ms", int((time.time() - start_time) * 1000))
                
                # Record success status
                span.set_status(Status(StatusCode.OK))
                
                # Add result if relevant
                if result is not None:
                    set_span_attribute(span, "agno.memory.result", str(result))
                
                return result
            
            except Exception as err:
                # Record the exception
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise
    
    return traced_method


class AgnoSpanAttributes:
    """
    Helper class to extract and set Agno Agent attributes on spans.
    """
    
    def __init__(self, span: Span, instance: Any) -> None:
        """
        Initialize with a span and Agno instance.
        
        Args:
            span: OpenTelemetry span to update
            instance: Agno Agent instance
        """
        self.span = span
        self.instance = instance
        self.agent_data = {}
        
        self.run()
    
    def run(self) -> None:
        """Process the instance attributes and add them to the span."""
        # Collect basic agent attributes
        self.collect_agent_attributes()
        
        # Add attributes to span
        for key, value in self.agent_data.items():
            if value is not None:
                set_span_attribute(
                    self.span, 
                    f"agno.agent.{key}", 
                    str(value) if not isinstance(value, (int, float, bool)) else value
                )
    
    def collect_agent_attributes(self) -> None:
        """Collect important attributes from the Agent instance."""
        # Extract basic agent information
        if hasattr(self.instance, "agent_id"):
            self.agent_data["id"] = self.instance.agent_id
        
        if hasattr(self.instance, "name"):
            self.agent_data["name"] = self.instance.name
        
        if hasattr(self.instance, "session_id"):
            self.agent_data["session_id"] = self.instance.session_id
        
        if hasattr(self.instance, "user_id"):
            self.agent_data["user_id"] = self.instance.user_id
        
        if hasattr(self.instance, "run_id"):
            self.agent_data["run_id"] = self.instance.run_id
        
                        # Extract model information
        if hasattr(self.instance, "model") and self.instance.model:
            model = self.instance.model
            model_info = {}
            
            if hasattr(model, "id"):
                model_info["id"] = model.id
            
            if hasattr(model, "name"):
                model_info["name"] = model.name
                
            if hasattr(model, "provider"):
                model_info["provider"] = model.provider
                
            # Add temperature if available
            if hasattr(model, "temperature") and model.temperature is not None:
                model_info["temperature"] = model.temperature
                
            # Add max_tokens if available
            if hasattr(model, "max_tokens") and model.max_tokens is not None:
                model_info["max_tokens"] = model.max_tokens
            
            self.agent_data["model"] = json.dumps(model_info)
        
        # Extract tool information
        if hasattr(self.instance, "tools") and self.instance.tools:
            tool_info = []
            for tool in self.instance.tools:
                tool_data = {}
                
                # Handle different types of tools
                if hasattr(tool, "name"):
                    tool_data["name"] = tool.name
                    
                    # Handle DuckDuckGoTools and similar toolkits
                    if hasattr(tool, "functions") and isinstance(tool.functions, dict):
                        tool_data["functions"] = list(tool.functions.keys())
                        
                elif hasattr(tool, "__name__"):
                    tool_data["name"] = tool.__name__
                else:
                    tool_data["name"] = str(tool)
                
                # Add functions if available
                if not "functions" in tool_data and hasattr(tool, "functions"):
                    if callable(getattr(tool, "functions")):
                        try:
                            tool_functions = tool.functions()
                            if isinstance(tool_functions, list):
                                tool_data["functions"] = [f.__name__ if hasattr(f, "__name__") else str(f) 
                                                         for f in tool_functions]
                        except:
                            pass
                
                tool_info.append(tool_data)
            
            self.agent_data["tools"] = json.dumps(tool_info)
        
        # Extract reasoning settings
        if hasattr(self.instance, "reasoning") and self.instance.reasoning:
            self.agent_data["reasoning_enabled"] = True
            
            if hasattr(self.instance, "reasoning_model") and self.instance.reasoning_model:
                self.agent_data["reasoning_model"] = str(self.instance.reasoning_model.id)
            
            if hasattr(self.instance, "reasoning_min_steps"):
                self.agent_data["reasoning_min_steps"] = self.instance.reasoning_min_steps
                
            if hasattr(self.instance, "reasoning_max_steps"):
                self.agent_data["reasoning_max_steps"] = self.instance.reasoning_max_steps
        
        # Extract knowledge settings
        if hasattr(self.instance, "knowledge") and self.instance.knowledge:
            self.agent_data["knowledge_enabled"] = True
        
        # Extract streaming settings
        if hasattr(self.instance, "stream"):
            self.agent_data["stream"] = self.instance.stream