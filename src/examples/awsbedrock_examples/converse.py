import boto3
import json
from langtrace_python_sdk import langtrace
from dotenv import load_dotenv
import botocore
from langchain_aws import ChatBedrock

load_dotenv()
langtrace.init(write_spans_to_console=False)

brt = boto3.client("bedrock-runtime", region_name="us-east-1")
brc = boto3.client("bedrock", region_name="us-east-1")


def use_converse_stream():
    model_id = "anthropic.claude-3-haiku-20240307-v1:0"
    conversation = [
        {
            "role": "user",
            "content": [{"text": "what is the capital of France?"}],
        }
    ]

    try:
        response = brt.converse_stream(
            modelId=model_id,
            messages=conversation,
            inferenceConfig={"maxTokens": 4096, "temperature": 0},
            additionalModelRequestFields={"top_k": 250},
        )
        # response_text = response["output"]["message"]["content"][0]["text"]
        print(response)

    except Exception as e:
        print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
        exit(1)


def use_converse():
    model_id = "anthropic.claude-3-haiku-20240307-v1:0"
    conversation = [
        {
            "role": "user",
            "content": [{"text": "what is the capital of France?"}],
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
    for model in brc.list_foundation_models()["modelSummaries"]:
        print(model["modelId"])


# Invoke Model API
# Amazon Titan Models
def use_invoke_model_titan(stream=False):
    try:
        prompt_data = "what's the capital of France?"
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

        if stream:

            response = brt.invoke_model_with_response_stream(
                body=body, modelId=modelId, accept=accept, contentType=contentType
            )
            # Extract and print the response text in real-time.
            for event in response["body"]:
                chunk = json.loads(event["chunk"]["bytes"])
                if "outputText" in chunk:
                    print(chunk["outputText"], end="")

        else:
            response = brt.invoke_model(
                body=body, modelId=modelId, accept=accept, contentType=contentType
            )
            response_body = json.loads(response.get("body").read())

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
def use_invoke_model_anthropic(stream=False):
    body = json.dumps(
        {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "temperature": 0.1,
            "top_p": 0.9,
            "messages": [{"role": "user", "content": "Hello, Claude"}],
        }
    )
    modelId = "anthropic.claude-v2"
    accept = "application/json"
    contentType = "application/json"

    if stream:
        response = brt.invoke_model_with_response_stream(body=body, modelId=modelId)
        stream_response = response.get("body")
        if stream_response:
            for event in stream_response:
                chunk = event.get("chunk")
                if chunk:
                    # print(json.loads(chunk.get("bytes").decode()))
                    pass

    else:
        response = brt.invoke_model(
            body=body, modelId=modelId, accept=accept, contentType=contentType
        )
        response_body = json.loads(response.get("body").read())
        # text
        print(response_body.get("completion"))


def use_invoke_model_llama(stream=False):
    model_id = "meta.llama3-8b-instruct-v1:0"
    prompt = "What is the capital of France?"
    max_gen_len = 128
    temperature = 0.1
    top_p = 0.9

    # Create request body.
    body = json.dumps(
        {
            "prompt": prompt,
            "max_gen_len": max_gen_len,
            "temperature": temperature,
            "top_p": top_p,
        }
    )

    if stream:
        response = brt.invoke_model_with_response_stream(body=body, modelId=model_id)
        for event in response["body"]:
            chunk = json.loads(event["chunk"]["bytes"])
            if "generation" in chunk:
                # print(chunk["generation"], end="")
                pass
    else:
        response = brt.invoke_model(body=body, modelId=model_id)
        response_body = json.loads(response.get("body").read())
        return response_body


# print(get_foundation_models())
def use_invoke_model_cohere():
    model_id = "cohere.command-r-plus-v1"
    prompt = "What is the capital of France?"
    body = json.dumps({"prompt": prompt, "max_tokens": 1024, "temperature": 0.1})
    response = brt.invoke_model(body=body, modelId=model_id)
    response_body = json.loads(response.get("body").read())
    print(response_body)


def init_bedrock_langchain(temperature=0.1):
    chat = ChatBedrock(
        model_id="anthropic.claude-v2",
        streaming=True,
        model_kwargs={"temperature": temperature},
        region_name="us-east-1",
    )
    return chat.invoke("What is the capital of France?")
