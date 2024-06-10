from typing import Optional, Sequence
from colorama import Fore
from opentelemetry.sdk.trace import sampling
from opentelemetry.sdk.trace.sampling import (
    Sampler,
    Decision,
    SamplingResult,
    ParentBased,
    ALWAYS_ON,
    ALWAYS_OFF,
)
from opentelemetry.trace import SpanKind, Link, TraceState, TraceFlags, get_current_span
from opentelemetry.util.types import Attributes
from opentelemetry.context import Context
from opentelemetry import trace
from opentelemetry.sdk.trace import ReadableSpan


class LangtraceSampler(Sampler):
    _disabled_methods_names: set
    _seen: set = set()

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

        if not trace_state:
            trace_state = TraceState([("langtrace.sampling", "disabled")])
        trace_state.add("langtrace.sampling", "disabled")

        print(Fore.GREEN + f"Sampling span(s) related to {name}" + Fore.RESET)
        print(
            Fore.BLUE
            + f"Span Context: {trace.get_current_span().get_span_context()}"
            + Fore.RESET
        )
        print(Fore.BLUE + f"p Context: {parent_context}" + Fore.RESET)
        print("\n")
        span = trace.get_current_span()
        span_context = span.get_span_context()

        if not self._disabled_methods_names:
            return SamplingResult(
                decision=Decision.RECORD_AND_SAMPLE,
                trace_state=trace_state,
                attributes=attributes,
            )

        # Check if the span name is in the disabled methods list
        if name in self._disabled_methods_names:
            print(
                Fore.RED
                + f"Skipping sampling span(s) related to {name} as it's disabled"
                + Fore.RESET
            )

            self._seen.add(span_context.span_id)
            print(Fore.RED + f"Seen: {self._seen}" + Fore.RESET)
            return SamplingResult(decision=Decision.DROP, trace_state=trace_state)

        return SamplingResult(
            decision=Decision.RECORD_AND_SAMPLE, trace_state=trace_state
        )

    def get_description(self):
        return "LangtraceSampler"
