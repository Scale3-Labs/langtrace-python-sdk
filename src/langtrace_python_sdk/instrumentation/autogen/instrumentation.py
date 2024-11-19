from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import get_tracer
from wrapt import wrap_function_wrapper as _W
from importlib_metadata import version as v
from .patch import (
    patch_generate_reply,
    patch_initiate_chat,
    patch_group_chat_init,
    patch_function_call
)


class AutogenInstrumentation(BaseInstrumentor):
    def instrumentation_dependencies(self):
        return ["autogen >= 0.1.0"]

    def _instrument(self, **kwargs):
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, "", tracer_provider)
        version = v("autogen")
        try:
            _W(
                module="autogen.agentchat.conversable_agent",
                name="ConversableAgent.initiate_chat",
                wrapper=patch_initiate_chat(
                    "conversable_agent.initiate_chat", version, tracer
                ),
            )

            _W(
                module="autogen.agentchat.conversable_agent",
                name="ConversableAgent.generate_reply",
                wrapper=patch_generate_reply(
                    "conversable_agent.generate_reply", version, tracer
                ),
            )

            _W(
                module="autogen.agentchat.groupchat",
                name="GroupChat.__init__",
                wrapper=patch_group_chat_init(
                    "groupchat.init", version, tracer
                ),
            )

            _W(
                module="autogen.agentchat.conversable_agent",
                name="ConversableAgent._call_function",
                wrapper=patch_function_call(
                    "conversable_agent.call_function", version, tracer
                ),
            )
        except Exception as e:
            pass

    def _uninstrument(self, **kwargs):
        pass
