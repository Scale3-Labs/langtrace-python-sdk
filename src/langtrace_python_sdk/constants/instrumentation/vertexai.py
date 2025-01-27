APIS = {
    "GENERATE_CONTENT": {
        "module": "vertexai.generative_models",
        "method": "GenerativeModel",
        "operation": "generate_content",
    },
    "AGENERATE_CONTENT": {
        "module": "vertexai.generative_models",
        "method": "GenerativeModel",
        "operation": "generate_content_async",
    },
    "PREDICT": {
        "module": "vertexai.language_models",
        "method": "TextGenerationModel",
        "operation": "predict",
    },
    "APREDICT": {
        "module": "vertexai.language_models",
        "method": "TextGenerationModel",
        "operation": "predict_async",
    },
    "PREDICT_STREAM": {
        "module": "vertexai.language_models",
        "method": "TextGenerationModel",
        "operation": "predict_streaming",
    },
    "APREDICT_STREAM": {
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
    "PREDICTION_SERVICE_BETA_GENERATE_CONTENT": {
        "module": "google.cloud.aiplatform_v1beta1.services.prediction_service.client",
        "method": "PredictionServiceClient",
        "operation": "generate_content",
    },
    "PREDICTION_SERVICE_GENERATE_CONTENT": {
        "module": "google.cloud.aiplatform_v1.services.prediction_service.client",
        "method": "PredictionServiceClient",
        "operation": "generate_content",
    },
    "PREDICTION_SERVICE_BETA_STREAM_GENERATE_CONTENT": {
        "module": "google.cloud.aiplatform_v1beta1.services.prediction_service.client",
        "method": "PredictionServiceClient",
        "operation": "stream_generate_content",
    },
    "PREDICTION_SERVICE_STREAM_GENERATE_CONTENT": {
        "module": "google.cloud.aiplatform_v1.services.prediction_service.client",
        "method": "PredictionServiceClient",
        "operation": "stream_generate_content",
    },
}
