import os
import boto3
from langtrace_python_sdk import langtrace

langtrace.init(api_key=os.environ["LANGTRACE_API_KEY"])

def use_converse():
    model_id = "anthropic.claude-3-haiku-20240307-v1:0"
    client = boto3.client(
        "bedrock-runtime",
        region_name="us-east-1",
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    )
    conversation = [
        {
            "role": "user",
            "content": [{"text": "Write a story about a magic backpack."}],
        }
    ]

    try:
        response = client.converse(
            modelId=model_id,
            messages=conversation,
            inferenceConfig={"maxTokens":4096,"temperature":0},
            additionalModelRequestFields={"top_k":250}
        )
        response_text = response["output"]["message"]["content"][0]["text"]
        print(response_text)

    except (Exception) as e:
        print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
        exit(1)