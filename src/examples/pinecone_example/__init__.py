from langtrace_python_sdk import (
    get_prompt_from_registry,
    with_langtrace_root_span,
    with_additional_attributes,
    inject_additional_attributes,
)


class PineconeRunner:
    @with_langtrace_root_span("Pinecone")
    def run(self):
        from .basic import basic as do_llm_stuff

        response = inject_additional_attributes(do_llm_stuff, {"user.id": 1234})
        print(response)
        return response
