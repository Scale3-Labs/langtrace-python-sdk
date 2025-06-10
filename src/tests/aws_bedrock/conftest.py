"""Unit tests configuration module."""

import pytest
import os

from boto3.session import Session
from botocore.config import Config

from langtrace_python_sdk.instrumentation.aws_bedrock.instrumentation import (
    AWSBedrockInstrumentation,
)


@pytest.fixture(autouse=True)
def environment():
    if not os.getenv("AWS_ACCESS_KEY_ID"):
        os.environ["AWS_ACCESS_KEY_ID"] = "test_api_key"


@pytest.fixture
def aws_bedrock_client():
    bedrock_config = Config(
        region_name="us-east-1",
        connect_timeout=300,
        read_timeout=300,
        retries={"total_max_attempts": 2, "mode": "standard"},
    )
    return Session().client("bedrock-runtime", config=bedrock_config)


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [
            "authorization",
            "X-Amz-Date",
            "X-Amz-Security-Token",
            "amz-sdk-invocation-id",
            "amz-sdk-request",
        ]
    }


@pytest.fixture(scope="session", autouse=True)
def instrument():
    AWSBedrockInstrumentation().instrument()
