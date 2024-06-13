from typing import Optional, Sequence
from opentelemetry.sdk.trace.sampling import (
    Sampler,
    Decision,
    SamplingResult,
)
from opentelemetry.trace import SpanKind, Link, TraceState, TraceFlags
from opentelemetry.util.types import Attributes
from opentelemetry.context import Context
from opentelemetry import trace


class LangtraceSampler(Sampler):
    _disabled_methods_names: set

    def __init__(
        self,
        disabled_methods: dict,
    ):
        self._disabled_methods_names = set()
        if disabled_methods:
            for _, methods in disabled_methods.items():
                for method in methods:
                    self._disabled_methods_names.add(method)

    def should_sample(
        self,
        parent_context: Optional[Context],
        trace_id: int,
        name: str,
        kind: Optional[SpanKind] = None,
        attributes: Attributes = None,
        links: Optional[Sequence[Link]] = None,
        trace_state: Optional["TraceState"] = None,
    ) -> SamplingResult:

        parent_span = trace.get_current_span(parent_context)
        parent_span_context = parent_span.get_span_context()

        if not self._disabled_methods_names:
            return SamplingResult(decision=Decision.RECORD_AND_SAMPLE)

        if parent_context:
            if (
                parent_span_context.span_id != 0
                and parent_span_context.trace_flags != TraceFlags.SAMPLED
            ):
                return SamplingResult(decision=Decision.DROP)

        if name in self._disabled_methods_names:
            return SamplingResult(decision=Decision.DROP)

        return SamplingResult(decision=Decision.RECORD_AND_SAMPLE)

    def get_description(self):
        return "Langtrace Sampler"
