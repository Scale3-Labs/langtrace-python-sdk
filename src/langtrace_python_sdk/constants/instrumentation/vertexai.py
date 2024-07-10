APIS = {
    "GENERATE_CONTENT": {
        "module": "vertexai.preview.generative_models",
        "method": "GenerativeModel",
        "operation": "generate_content",
    },
    "AGENERATE_CONTENT": {
        "module": "vertexai.preview.generative_models",
        "method": "GenerativeModel",
        "operation": "generate_content_async",
    },
    "PREDIT": {
        "module": "vertexai.language_models",
        "method": "TextGenerationModel",
        "operation": "predict",
    },
    "apredict": {
        "module": "vertexai.language_models",
        "method": "TextGenerationModel",
        "operation": "predict_async",
    },
    "PREDICT_STREAM": {
        "module": "vertexai.language_models",
        "method": "TextGenerationModel",
        "operation": "predict_streaming",
    },
    "apredict_STREAM": {
        "module": "vertexai.language_models",
        "method": "TextGenerationModel",
        "operation": "predict_streaming_async",
    },
    "SEND_MESSAGE": {
        "module": "vertexai.language_models",
        "method": "ChatSession",
        "operation": "send_message",
    },
    "send_message_streaming": {
        "module": "vertexai.language_models",
        "method": "ChatSession",
        "operation": "send_message_streaming",
    },
}
