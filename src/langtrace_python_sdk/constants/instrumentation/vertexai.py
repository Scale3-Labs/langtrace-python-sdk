APIS = [
    {
        "module": "vertexai.preview.generative_models",
        "name": "GenerativeModel",
        "method": "generate_content",
        "span_name": "vertexai.generate_content",
    },
    {
        "module": "vertexai.preview.generative_models",
        "name": "GenerativeModel",
        "method": "generate_content_async",
        "span_name": "vertexai.generate_content_async",
    },
    {
        "module": "vertexai.language_models",
        "name": "TextGenerationModel",
        "method": "predict",
        "span_name": "vertexai.predict",
    },
    {
        "module": "vertexai.language_models",
        "name": "TextGenerationModel",
        "method": "predict_async",
        "span_name": "vertexai.predict_async",
    },
    {
        "module": "vertexai.language_models",
        "name": "TextGenerationModel",
        "method": "predict_streaming",
        "span_name": "vertexai.predict_streaming",
    },
    {
        "module": "vertexai.language_models",
        "name": "TextGenerationModel",
        "method": "predict_streaming_async",
        "span_name": "vertexai.predict_streaming_async",
    },
    {
        "module": "vertexai.language_models",
        "name": "ChatSession",
        "method": "send_message",
        "span_name": "vertexai.send_message",
    },
    {
        "module": "vertexai.language_models",
        "name": "ChatSession",
        "method": "send_message_streaming",
        "span_name": "vertexai.send_message_streaming",
    },
]
