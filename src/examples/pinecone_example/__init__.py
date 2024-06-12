from langtrace_python_sdk import (
    get_prompt_from_registry,
    with_langtrace_root_span,
    with_additional_attributes,
)


class PineconeRunner:
    @with_langtrace_root_span("Pinecone")
    def run(self):
        from .basic import basic as basic_app

        res = get_prompt_from_registry("clxadbzv6000110n5z1ym58pg")

        with_additional_attributes(basic_app, {"prompt_id": res})
