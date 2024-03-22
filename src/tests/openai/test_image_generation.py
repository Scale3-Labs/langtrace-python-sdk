import pytest
from unittest.mock import MagicMock, Mock, patch, call
from langtrace_python_sdk.instrumentation.openai.patch import images_generate
from opentelemetry.trace import SpanKind
from opentelemetry.trace import get_tracer
import importlib.metadata
import openai
from langtrace_python_sdk.constants.instrumentation.openai import APIS
from opentelemetry.trace import SpanKind
from opentelemetry.trace.status import Status, StatusCode

import json

class TestImageGeneration():
    data = {
  "created": 1710983755,
  "data": [
    {
      "b64_json": "null",
      "revised_prompt": "A charming and adorable baby sea otter. This small, fluffy creature is floating gracefully on its back, with its tiny webbed paws folded cutely over its fuzzy belly. It has big, round, innocent eyes that are brimming with youthful curiosity. As it blissfully floats on the calm, sparkling ocean surface under the glow of the golden sunset, it playfully tosses a shiny seashell from one paw to another, showcasing its playful and distinctively otter-like behavior.",
      "url": "https://oaidalleapiprodscus.blob.core.windows.net/private/org-Bj6XXxxFgkJeYFnhs2nXl0nr/user-HqmprrkKKvVVzITKBT4hXs1S/img-8soh2bwtO1XFOikrFOys1t2y.png?st=2024-03-21T00%3A15%3A55Z&se=2024-03-21T02%3A15%3A55Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2024-03-20T23%3A21%3A13Z&ske=2024-03-21T23%3A21%3A13Z&sks=b&skv=2021-08-06&sig=lNjMKuLvU4OytlYs7n6ZZN1McN9tBmcy4auiAaKRFAQ%3D"
    }
  ]
}

    @pytest.fixture
    def openai_mock(self):
        with patch('openai.images.generate') as mock_image_generate:
            mock_image_generate.return_value = json.dumps(self.data)  
            yield mock_image_generate
        

    @pytest.fixture
    def set_up(self):
        # Create a tracer provider
        self.tracer = Mock()
        self.span = Mock()

        # Create a context manager mock for start_as_current_span
        context_manager_mock = MagicMock()
        context_manager_mock.__enter__.return_value = self.span
        self.tracer.start_as_current_span.return_value = context_manager_mock
        
    @pytest.fixture
    def tear_down(self):
        # Perform clean-up operations here, if needed
        pass

    def test_image_generation(self, set_up, openai_mock, tear_down):
    
        # Arrange
        version = importlib.metadata.version('openai')
        llm_model_value = 'dall-e-3'
        prompt_value = "A cute baby sea otter"
        kwargs = {
            'model': llm_model_value,
            'prompt': prompt_value,
        }

        # Act
        wrapped_function = images_generate(openai.images.generate, version, self.tracer)
        result = wrapped_function(Mock(), Mock(), (), kwargs)

        # Assert
        assert self.tracer.start_as_current_span.called_once_with("openai.images.generate", kind=SpanKind.CLIENT)

        expected_attributes = {
            "langtrace.service.name": 'OpenAI',
            "langtrace.service.type": "llm",
            "langtrace.service.version": version,
            "langtrace.version": "1.0.0",
            "url.full": 'https://api.openai.com/v1/',
            "llm.api": "images_generation_endpoint",  # Replace with the actual endpoint value
            "llm.model": kwargs.get('model'),
            "llm.stream": kwargs.get('stream'),  # The 'stream' key is not in kwargs, check if it should be included
            "llm.prompts": json.dumps([kwargs.get('prompt', [])])
        }
        assert self.span.set_attribute.has_calls([call(key, value) for key, value in expected_attributes.items()], any_order=True)
        assert self.span.set_status.called_once_with(Status(StatusCode.OK))

        expected_result = ['created', 'data']
        result_keys = json.loads(result).keys()
        assert set(expected_result) == set(result_keys), "Keys mismatch"

        revised_prompt = "A charming and adorable baby sea otter. This small, fluffy creature is floating gracefully on its back, with its tiny webbed paws folded cutely over its fuzzy belly. It has big, round, innocent eyes that are brimming with youthful curiosity. As it blissfully floats on the calm, sparkling ocean surface under the glow of the golden sunset, it playfully tosses a shiny seashell from one paw to another, showcasing its playful and distinctively otter-like behavior."
        assert json.loads(result).get('data')[0].get('revised_prompt') == revised_prompt, "Content mismatch"