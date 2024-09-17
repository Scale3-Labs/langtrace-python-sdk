from langtrace_python_sdk.types import NOT_GIVEN, InstrumentationType
from .sdk_version_checker import SDKVersionChecker
from opentelemetry.trace import Span
from langtrace.trace_attributes import SpanAttributes
import inspect
import os


def set_span_attribute(span: Span, name, value):
    if value is not None:
        if value != "" or value != NOT_GIVEN:
            if name == SpanAttributes.LLM_PROMPTS:
                set_event_prompt(span, value)
            else:
                span.set_attribute(name, value)
    return


def set_event_prompt(span: Span, prompt):
    enabled = os.environ.get("TRACE_PROMPT_COMPLETION_DATA", "true")
    if enabled.lower() == "false":
        return

    span.add_event(
        name=SpanAttributes.LLM_CONTENT_PROMPT,
        attributes={
            SpanAttributes.LLM_PROMPTS: prompt,
        },
    )


def deduce_args_and_kwargs(func, *args, **kwargs):
    sig = inspect.signature(func)
    bound_args = sig.bind(*args, **kwargs)
    bound_args.apply_defaults()

    all_params = {}
    for param_name, param in sig.parameters.items():
        if param_name in bound_args.arguments:
            all_params[param_name] = bound_args.arguments[param_name]

    return all_params


def check_if_sdk_is_outdated():
    SDKVersionChecker().check()
    return


def get_sdk_version():
    return SDKVersionChecker().get_sdk_version()


def validate_instrumentations(disable_instrumentations):
    if disable_instrumentations is not None:
        if (
            disable_instrumentations.get("all_except") is not None
            and disable_instrumentations.get("only") is not None
        ):
            raise ValueError(
                "Cannot specify both only and all_except in disable_instrumentations"
            )

        for key, value in disable_instrumentations.items():
            if isinstance(value, str):
                # Convert single string to list of enum values
                disable_instrumentations[key] = [InstrumentationType.from_string(value)]
            elif isinstance(value, list):
                # Convert list of strings to list of enum values
                disable_instrumentations[key] = [
                    (
                        InstrumentationType.from_string(item)
                        if isinstance(item, str)
                        else item
                    )
                    for item in value
                ]
            # Validate all items are of enum type
            if not all(
                isinstance(item, InstrumentationType)
                for item in disable_instrumentations[key]
            ):
                raise TypeError(
                    f"All items in {key} must be of type InstrumentationType"
                )


def is_package_installed(package_name):
    import pkg_resources

    installed_packages = {p.key for p in pkg_resources.working_set}
    return package_name in installed_packages
