from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import get_tracer
from wrapt import wrap_function_wrapper as _W
from importlib_metadata import version as v
from .patch import patch_autogen


class AutogenInstrumentation(BaseInstrumentor):
    def instrumentation_dependencies(self):
        return ["pyautogen >= 0.1.0"]

    def _instrument(self, **kwargs):
        print("Instrumneting autogen")
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, "", tracer_provider)
        version = v("pyautogen")
        # conversable_agent.intiate_chat
        # conversable_agent.register_function
        # agent.Agent
        # AgentCreation
        # Tools --> Register_for_llm, register_for_execution, register_for_function 
        try:
            _W(
                module="autogen.agentchat.conversable_agent",
                name="ConversableAgent.initiate_chat",
                wrapper=patch_autogen(
                    "conversable_agent.initiate_chat", version, tracer
                ),
            )

            _W(
                module="autogen.agentchat.conversable_agent",
                name="ConversableAgent.generate_reply",
                wrapper=patch_autogen(
                    "conversable_agent.generate_reply", version, tracer
                ),
            )
        except Exception as e:
            print(e)

    def _uninstrument(self, **kwargs):
        pass
