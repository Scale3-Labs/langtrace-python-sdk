import json
from importlib_metadata import version as v
from langtrace_python_sdk.constants import LANGTRACE_SDK_NAME
from langtrace_python_sdk.utils import set_span_attribute
from langtrace_python_sdk.utils.llm import get_span_name, set_span_attributes
from langtrace_python_sdk.constants.instrumentation.common import (
    LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY,
    SERVICE_PROVIDERS,
)
from opentelemetry import baggage
from langtrace.trace_attributes import FrameworkSpanAttributes
from opentelemetry.trace import SpanKind, Span, Tracer
from opentelemetry.trace.status import Status, StatusCode


crew_properties = {
    "tasks": "object",
    "agents": "object",
    "cache": "bool",
    "process": "object",
    "verbose": "bool",
    "memory": "bool",
    "embedder": "json",
    "full_output": "bool",
    "manager_llm": "object",
    "manager_agent": "object",
    "manager_callbacks": "object",
    "function_calling_llm": "object",
    "config": "json",
    "id": "object",
    "max_rpm": "int",
    "share_crew": "bool",
    "step_callback": "object",
    "task_callback": "object",
    "prompt_file": "str",
    "output_log_file": "bool",
}

task_properties = {
    "id": "object",
    "used_tools": "int",
    "tools_errors": "int",
    "delegations": "int",
    "i18n": "object",
    "thread": "object",
    "prompt_context": "object",
    "description": "str",
    "expected_output": "str",
    "config": "object",
    "callback": "str",
    "agent": "object",
    "context": "object",
    "async_execution": "bool",
    "output_json": "object",
    "output_pydantic": "object",
    "output_file": "object",
    "output": "object",
    "tools": "object",
    "human_input": "bool",
}

agent_properties = {
    "formatting_errors": "int",
    "id": "object",
    "role": "str",
    "goal": "str",
    "backstory": "str",
    "cache": "bool",
    "config": "object",
    "max_rpm": "int",
    "verbose": "bool",
    "allow_delegation": "bool",
    "tools": "object",
    "max_iter": "int",
    "max_execution_time": "object",
    "agent_executor": "object",
    "tools_handler": "object",
    "force_answer_max_iterations": "int",
    "crew": "object",
    "cache_handler": "object",
    "step_callback": "object",
    "i18n": "object",
    "llm": "object",
    "function_calling_llm": "object",
    "callbacks": "object",
    "system_template": "object",
    "prompt_template": "object",
    "response_template": "object",
}


def patch_crew(operation_name, version, tracer: Tracer):
    def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS["CREWAI"]
        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)
        span_attributes = {
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "framework",
            "langtrace.service.version": version,
            "langtrace.version": v(LANGTRACE_SDK_NAME),
            **(extra_attributes if extra_attributes is not None else {}),
        }

        attributes = FrameworkSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(
            get_span_name(operation_name), kind=SpanKind.CLIENT
        ) as span:

            try:
                set_span_attributes(span, attributes)
                CrewAISpanAttributes(span=span, instance=instance)
                result = wrapped(*args, **kwargs)
                if result:
                    span.set_status(Status(StatusCode.OK))

                span.end()
                return result

            except Exception as err:
                print("Error", err)
                # Record the exception in the span
                span.record_exception(err)

                # Set the span status to indicate an error
                span.set_status(Status(StatusCode.ERROR, str(err)))

                # Reraise the exception to ensure it's not swallowed
                raise

    return traced_method


class CrewAISpanAttributes:
    span: Span
    crew: dict

    def __init__(self, span: Span, instance) -> None:
        self.span = span
        self.instance = instance
        self.crew = {
            "tasks": [],
            "agents": [],
        }

        self.run()

    def run(self):
        instance_name = self.instance.__class__.__name__
        if instance_name == "Crew":
            self.set_crew_attributes()
            set_span_attribute(self.span, "crewai.crew.config", json.dumps(self.crew))

        elif instance_name == "Agent":
            agent = self.set_agent_attributes()
            # for key, value in agent.items():
            #     set_span_attribute(self.span, key, value)
            set_span_attribute(self.span, "crewai.agent.config", json.dumps(agent))
        elif instance_name == "Task":
            task = self.set_task_attributes()
            # uncomment if you want to spread attributes for the UI instead of dumping the whole object
            # for key, value in task.items():
            #     set_span_attribute(self.span, key, value)
            set_span_attribute(self.span, "crewai.task.config", json.dumps(task))

    def set_crew_attributes(self):
        for key, value in self.instance.__dict__.items():
            if key == "tasks":
                self._parse_tasks(value)

            elif key == "agents":
                self._parse_agents(value)
            else:
                self.crew[key] = str(value)

    def set_agent_attributes(self):
        agent = {}
        for key, value in self.instance.__dict__.items():
            if value is None:
                continue
            agent[key] = str(value)

        return agent

    def set_task_attributes(self):
        task = {}
        for key, value in self.instance.__dict__.items():
            if value is None:
                continue

            if key == "agent":
                task[key] = value.role
            else:
                task[key] = str(value)
        return task

    def _parse_agents(self, agents):
        for agent in agents:
            self.crew["agents"].append(
                {
                    "id": str(agent.id),
                    "role": agent.role,
                    "goal": agent.goal,
                    "backstory": agent.backstory,
                    "cache": agent.cache,
                    "config": agent.config,
                    "verbose": agent.verbose,
                    "allow_delegation": agent.allow_delegation,
                    "tools": agent.tools,
                    "max_iter": agent.max_iter,
                    "llm": str(agent.llm.model),
                }
            )

    def _parse_tasks(self, tasks):
        for task in tasks:
            self.crew["tasks"].append(
                {
                    "agent": task.agent.role,
                    "description": task.description,
                    "async_execution": task.async_execution,
                    "expected_output": task.expected_output,
                    "human_input": task.human_input,
                    "tools": task.tools,
                    "output_file": task.output_file,
                }
            )
