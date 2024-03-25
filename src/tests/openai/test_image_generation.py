import unittest
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
from tests.utils import common_setup

class TestImageGeneration(unittest.TestCase):
    data = {
        "created": 1710983755,
        "data": [
            {
                "b64_json": "null",
                "revised_prompt": "A charming and adorable baby sea otter. This small, fluffy creature is floating gracefully on its back, with its tiny webbed paws folded cutely over its fuzzy belly. It has big, round, innocent eyes that are brimming with youthful curiosity. As it blissfully floats on the calm, sparkling ocean surface under the glow of the golden sunset, it playfully tosses a shiny seashell from one paw to another, showcasing its playful and distinctively otter-like behavior.",
                "url": "https://images.openai.com/sea-otter.jpg"
            }
        ]
    }

    def setUp(self):
        self.openai_mock, self.tracer, self.span = common_setup(self.data, 'openai.images.generate')


    def tearDown(self):
        self.openai_mock.stop()

    def test_image_generation(self):
        # Arrange
        version = importlib.metadata.version('openai')
        llm_model_value = 'dall-e-3'
        prompt_value = "A cute baby sea otter"
        kwargs = {
            'model': llm_model_value,
            'prompt': prompt_value,
            'stream': False        }

        # Act
        wrapped_function = images_generate(openai.images.generate, version, self.tracer)
        result = wrapped_function(MagicMock(), MagicMock(), (), kwargs)

        # Assert
        self.assertTrue(self.tracer.start_as_current_span.called_once_with("openai.images.generate", kind=SpanKind.CLIENT))

        expected_attributes = {
            "langtrace.service.name": 'OpenAI',
            "langtrace.service.type": "llm",
            "langtrace.service.version": version,
            "langtrace.version": "1.0.0",
            "url.full": 'https://api.openai.com/v1/',
            "llm.api": "images_generation_endpoint",  
            "llm.model": kwargs.get('model'),
            "llm.stream": kwargs.get('stream'),  
            "llm.prompts": json.dumps([kwargs.get('prompt', [])])
        }
        self.assertTrue(self.span.set_attribute.has_calls([call(key, value) for key, value in expected_attributes.items()], any_order=True))
        self.assertTrue(self.span.set_status.called_once_with(Status(StatusCode.OK)))

        expected_result = ['created', 'data']
        result_keys = json.loads(result).keys()
        self.assertSetEqual(set(expected_result), set(result_keys), "Keys mismatch")

        revised_prompt = "A charming and adorable baby sea otter. This small, fluffy creature is floating gracefully on its back, with its tiny webbed paws folded cutely over its fuzzy belly. It has big, round, innocent eyes that are brimming with youthful curiosity. As it blissfully floats on the calm, sparkling ocean surface under the glow of the golden sunset, it playfully tosses a shiny seashell from one paw to another, showcasing its playful and distinctively otter-like behavior."
        self.assertEqual(json.loads(result).get('data')[0].get('revised_prompt'), revised_prompt, "Content mismatch")
        
if __name__ == '__main__':
    unittest.main()