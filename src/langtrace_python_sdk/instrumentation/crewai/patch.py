import json
from importlib_metadata import version as v
from langtrace_python_sdk.constants import LANGTRACE_SDK_NAME
from langtrace_python_sdk.utils import set_span_attribute
from langtrace_python_sdk.utils.llm import get_span_name
from langtrace_python_sdk.utils.silently_fail import silently_fail
from langtrace_python_sdk.constants.instrumentation.common import (
    LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY,
    SERVICE_PROVIDERS,
)
from opentelemetry import baggage
from langtrace.trace_attributes import FrameworkSpanAttributes
from opentelemetry.trace import SpanKind
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


def parse_crewai_tasks(tasks):
    task_dict = {}
    for task in tasks:
        for key, value in task.__dict__.items():
            if value is None:
                continue

            elif key == "id":
                task_dict[key] = str(value)

            elif key == "agent":
                task_dict[key] = value.__dict__["role"]

            elif key in [
                "used_tools",
                "tools_errors",
                "delegations",
                "description",
                "expected_output",
                "human_input",
                "async_execution",
                "prompt_context",
                "expected_output",
                "output_file",
            ]:
                task_dict[key] = value
            else:
                task_dict[key] = str(value)
    return [task_dict]


def parse_crewai_agents(agents):
    agent_dict = {}
    for agent in agents:
        for key, value in agent.__dict__.items():
            if value is None:
                continue

            elif key == "id":
                agent_dict[key] = str(value)

            elif key in [
                "role" "formatting_errors",
                "goal",
                "backstory",
                "cache",
                "verbose",
                "max_rpm",
                "allow_delegation",
                "max_iter",
                "max_execution_time",
            ]:
                agent_dict[key] = value
            else:
                agent_dict[key] = str(value)
    return [agent_dict]


def set_crewai_attributes(instance):
    crew_config = {}
    class_name = instance.__class__.__name__
    for key, value in instance.__dict__.items():
        if value is None:
            continue

        if class_name == "Crew":
            set_crew_attributes(key, value, crew_config)
        elif class_name == "Agent":
            set_agent_attributes(key, value, crew_config)
        elif class_name == "Task":
            set_task_attributes(key, value, crew_config)

    return crew_config


def set_crew_attributes(key, value, config: dict):
    if key not in crew_properties:
        return

    if key == "tasks":
        config[key] = parse_crewai_tasks(value)

    if key == "agents":
        config[key] = parse_crewai_agents(value)

    # if crew_properties[key] == "json":
    #     config[key] = json.dumps(value)
    # elif crew_properties[key] == "object":
    #     config[key] = str(value)
    # else:
    #     config[key] = value


def set_agent_attributes(key, value, config: dict):
    if key not in agent_properties:
        return

    if agent_properties[key] == "json":
        config[key] = json.dumps(value)
    elif agent_properties[key] == "object":
        config[key] = str(value)
    else:
        config[key] = value


def set_task_attributes(key, value, config: dict):
    if key not in task_properties:
        return

    if task_properties[key] == "json":
        config[key] = json.dumps(value)
    elif task_properties[key] == "object":
        config[key] = str(value)
    else:
        config[key] = value


def patch_crew(operation_name, version, tracer):
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

        crew_config = set_crewai_attributes(instance)

        if crew_config:
            if instance.__class__.__name__ == "Crew":
                if "inputs" in kwargs and kwargs["inputs"]:
                    crew_config["inputs"] = json.dumps(kwargs["inputs"])
                span_attributes["crewai.crew.config"] = json.dumps(crew_config)
            elif instance.__class__.__name__ == "Agent":
                if "context" in kwargs and kwargs["context"]:
                    crew_config["context"] = json.dumps(kwargs["context"])
                span_attributes["crewai.agent.config"] = json.dumps(crew_config)
            elif instance.__class__.__name__ == "Task":
                span_attributes["crewai.task.config"] = json.dumps(crew_config)

        attributes = FrameworkSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(
            get_span_name(operation_name), kind=SpanKind.CLIENT
        ) as span:
            _set_input_attributes(span, kwargs, attributes)

            try:
                result = wrapped(*args, **kwargs)
                if result:
                    span.set_status(Status(StatusCode.OK))

                span.end()
                return result

            except Exception as err:
                # Record the exception in the span
                span.record_exception(err)

                # Set the span status to indicate an error
                span.set_status(Status(StatusCode.ERROR, str(err)))

                # Reraise the exception to ensure it's not swallowed
                raise

    return traced_method


@silently_fail
def _set_input_attributes(span, kwargs, attributes):
    for field, value in attributes.model_dump(by_alias=True).items():
        set_span_attribute(span, field, value)
