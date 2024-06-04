import pytest
import json
from langtrace_python_sdk.constants.instrumentation.openai import APIS
from importlib_metadata import version as v


@pytest.mark.vcr()
def test_image_generation(openai_client, exporter):
    llm_model_value = "dall-e-3"
    prompt = "A charming and adorable baby sea otter. This small, fluffy creature is floating gracefully on its back, with its tiny webbed paws folded cutely over its fuzzy belly. It has big, round, innocent eyes that are brimming with youthful curiosity. As it blissfully floats on the calm, sparkling ocean surface under the glow of the golden sunset, it playfully tosses a shiny seashell from one paw to another, showcasing its playful and distinctively otter-like behavior."

    kwargs = {
        "model": llm_model_value,
        "prompt": prompt,
    }

    response = openai_client.images.generate(**kwargs)
    spans = exporter.get_finished_spans()
    image_generation_span = spans[-1]
    assert image_generation_span.name == "openai.images.generate"

    attributes = image_generation_span.attributes
    assert attributes.get("langtrace.sdk.name") == "langtrace-python-sdk"
    assert attributes.get("langtrace.service.name") == "OpenAI"
    assert attributes.get("langtrace.service.type") == "llm"
    assert attributes.get("langtrace.service.version") == v("openai")
    assert attributes.get("langtrace.version") == v("langtrace-python-sdk")
    assert attributes.get("url.full") == "https://api.openai.com/v1/"
    assert attributes.get("llm.api") == APIS["IMAGES_GENERATION"]["ENDPOINT"]
    assert attributes.get("llm.model") == llm_model_value
    prompts = json.loads(attributes.get("llm.prompts"))
    assert prompts[0]["content"] == prompt

    langtrace_responses = json.loads(attributes.get("llm.responses"))
    assert isinstance(langtrace_responses, list)
    for langtrace_response in langtrace_responses:
        assert isinstance(langtrace_response, dict)
        assert "role" in langtrace_response
        assert "content" in langtrace_response
        assert response.data[0].url == langtrace_response["content"]["url"]
        assert (
            response.data[0].revised_prompt
            == langtrace_response["content"]["revised_prompt"]
        )


@pytest.mark.vcr()
@pytest.mark.asyncio()
async def test_async_image_generation(async_openai_client, exporter):
    llm_model_value = "dall-e-3"
    prompt = "A charming and adorable baby sea otter. This small, fluffy creature is floating gracefully on its back, with its tiny webbed paws folded cutely over its fuzzy belly. It has big, round, innocent eyes that are brimming with youthful curiosity. As it blissfully floats on the calm, sparkling ocean surface under the glow of the golden sunset, it playfully tosses a shiny seashell from one paw to another, showcasing its playful and distinctively otter-like behavior."

    kwargs = {
        "model": llm_model_value,
        "prompt": prompt,
    }

    response = await async_openai_client.images.generate(**kwargs)
    spans = exporter.get_finished_spans()
    image_generation_span = spans[-1]
    assert image_generation_span.name == "openai.images.generate"

    attributes = image_generation_span.attributes
    assert attributes.get("langtrace.sdk.name") == "langtrace-python-sdk"
    assert attributes.get("langtrace.service.name") == "OpenAI"
    assert attributes.get("langtrace.service.type") == "llm"
    assert attributes.get("langtrace.service.version") == v("openai")
    assert attributes.get("langtrace.version") == v("langtrace-python-sdk")
    assert attributes.get("url.full") == "https://api.openai.com/v1/"
    assert attributes.get("llm.api") == APIS["IMAGES_GENERATION"]["ENDPOINT"]
    assert attributes.get("llm.model") == llm_model_value
    prompts = json.loads(attributes.get("llm.prompts"))
    assert prompts[0]["content"] == prompt

    langtrace_responses = json.loads(attributes.get("llm.responses"))
    assert isinstance(langtrace_responses, list)
    for langtrace_response in langtrace_responses:
        assert isinstance(langtrace_response, dict)
        assert "role" in langtrace_response
        assert "content" in langtrace_response
        assert response.data[0].url == langtrace_response["content"]["url"]
        assert (
            response.data[0].revised_prompt
            == langtrace_response["content"]["revised_prompt"]
        )
