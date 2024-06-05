"""
Copyright (c) 2024 Scale3 Labs

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

import asyncio
import os
from functools import wraps
from typing import Optional

import requests
from opentelemetry import baggage, context, trace
from opentelemetry.trace import SpanKind

from langtrace_python_sdk.constants.exporter.langtrace_exporter import (
    LANGTRACE_REMOTE_URL,
)
from langtrace_python_sdk.constants.instrumentation.common import (
    LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY,
)
from langtrace_python_sdk.utils.types import (
    EvaluationAPIData,
    LangTraceApiError,
    LangTraceEvaluation,
)
from colorama import Fore


def with_langtrace_root_span(
    name="LangtraceRootSpan",
    kind=SpanKind.INTERNAL,
):

    def decorator(func):
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            tracer = trace.get_tracer(__name__)
            operation_name = name if name else func.__name__
            span_id = None
            trace_id = None

            with tracer.start_as_current_span(operation_name, kind=kind) as span:
                span_id = str(span.get_span_context().span_id)
                trace_id = str(span.get_span_context().trace_id)

                if (
                    "span_id" in func.__code__.co_varnames
                    and "trace_id" in func.__code__.co_varnames
                ):
                    return func(*args, span_id, trace_id, **kwargs)
                else:
                    return func(*args, **kwargs)

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            span_id = None
            trace_id = None
            tracer = trace.get_tracer(__name__)
            operation_name = name if name else func.__name__
            with tracer.start_as_current_span(operation_name, kind=kind) as span:
                span_id = span.get_span_context().span_id
                trace_id = span.get_span_context().trace_id
                if (
                    "span_id" in func.__code__.co_varnames
                    and "trace_id" in func.__code__.co_varnames
                ):
                    return await func(*args, span_id, trace_id, **kwargs)
                else:
                    return await func(*args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def with_additional_attributes(attributes={}):
    def decorator(func):
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            new_ctx = baggage.set_baggage(
                LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY, attributes
            )
            context.attach(new_ctx)
            return func(*args, **kwargs)

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            new_ctx = baggage.set_baggage(
                LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY, attributes
            )
            context.attach(new_ctx)
            return await func(*args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


class SendUserFeedback:
    _langtrace_host: str
    _langtrace_api_key: str

    def __init__(self):
        self._langtrace_host = os.environ["LANGTRACE_API_HOST"]
        self._langtrace_api_key = os.environ.get("LANGTRACE_API_KEY", None)

    def evaluate(self, data: EvaluationAPIData) -> None:
        try:
            if self._langtrace_api_key is None:
                print(Fore.RED)
                print(
                    f"Missing Langtrace API key, proceed to {self._langtrace_host} to create one"
                )
                print("Set the API key as an environment variable LANGTRACE_API_KEY")
                print(Fore.RESET)
                return
            evaluation = self.get_evaluation(data["spanId"])
            headers = {"x-api-key": self._langtrace_api_key}
            if evaluation is not None:
                # Make a PUT request to update the evaluation
                print(Fore.BLUE + "Updating Feedback.." + Fore.RESET)
                response = requests.put(
                    f"{self._langtrace_host}/api/evaluation",
                    json=data,
                    params={"spanId": data["spanId"]},
                    headers=headers,
                    timeout=None,
                )
                response.raise_for_status()

            else:
                print(Fore.BLUE + "Sending User Feedback.." + Fore.RESET)
                # Make a POST request to create a new evaluation
                response = requests.post(
                    f"{self._langtrace_host}/api/evaluation",
                    json=data,
                    params={"spanId": data["spanId"]},
                    headers=headers,
                    timeout=None,
                )
                response.raise_for_status()

        except requests.RequestException as err:
            if err.response is not None:
                message = (
                    err.response.json().get("message", "")
                    if err.response.json().get("message", "")
                    else err.response.text if err.response.text else str(err)
                )
                raise LangTraceApiError(message, err.response.status_code)
            raise LangTraceApiError(str(err), 500)

    def get_evaluation(self, span_id: str) -> Optional[LangTraceEvaluation]:
        try:
            response = requests.get(
                f"{self._langtrace_host}/api/evaluation",
                params={"spanId": span_id},
                headers={"x-api-key": self._langtrace_api_key},
                timeout=None,
            )
            evaluations = response.json().get("evaluations", [])
            response.raise_for_status()
            return None if not evaluations else evaluations[0]

        except requests.RequestException as err:
            if err.response is not None:
                message = (
                    err.response.json().get("message", "")
                    if err.response.json().get("message", "")
                    else err.response.text if err.response.text else str(err)
                )
                raise LangTraceApiError(message, err.response.status_code)
            raise LangTraceApiError(str(err), 500)
