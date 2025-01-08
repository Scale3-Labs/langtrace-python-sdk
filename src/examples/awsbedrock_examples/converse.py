import boto3
import botocore
import json
from langtrace_python_sdk import langtrace
from dotenv import load_dotenv


load_dotenv()
langtrace.init()

brt = boto3.client("bedrock-runtime", region_name="us-east-1")
brc = boto3.client("bedrock", region_name="us-east-1")


def use_converse():
    model_id = "anthropic.claude-3-haiku-20240307-v1:0"
    conversation = [
        {
            "role": "user",
            "content": [{"text": "Write a story about a magic backpack."}],
        }
    ]

    try:
        response = brt.converse(
            modelId=model_id,
            messages=conversation,
            inferenceConfig={"maxTokens": 4096, "temperature": 0},
            additionalModelRequestFields={"top_k": 250},
        )
        response_text = response["output"]["message"]["content"][0]["text"]
        print(response_text)

    except Exception as e:
        print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
        exit(1)


def get_foundation_models():
    models = []
    for model in brc.list_foundation_models()["modelSummaries"]:
        models.append(model["modelId"])
    return models


# Invoke Model API
# Amazon Titan Models
def use_invoke_model_titan():
    try:
        prompt_data = "what's 1+1?"
        body = json.dumps(
            {
                "inputText": prompt_data,
                "textGenerationConfig": {
                    "maxTokenCount": 1024,
                    "topP": 0.95,
                    "temperature": 0.2,
                },
            }
        )
        modelId = "amazon.titan-text-express-v1"  # "amazon.titan-tg1-large"
        accept = "application/json"
        contentType = "application/json"

        response = brt.invoke_model(
            body=body, modelId=modelId, accept=accept, contentType=contentType
        )
        response_body = json.loads(response.get("body").read())

        # print(response_body.get("results"))

    except botocore.exceptions.ClientError as error:

        if error.response["Error"]["Code"] == "AccessDeniedException":
            print(
                f"\x1b[41m{error.response['Error']['Message']}\
                    \nTo troubeshoot this issue please refer to the following resources.\
                    \nhttps://docs.aws.amazon.com/IAM/latest/UserGuide/troubleshoot_access-denied.html\
                    \nhttps://docs.aws.amazon.com/bedrock/latest/userguide/security-iam.html\x1b[0m\n"
            )

        else:
            raise error


# Anthropic Models
def use_invoke_model_anthropic():
    pass


# print(get_foundation_models())
