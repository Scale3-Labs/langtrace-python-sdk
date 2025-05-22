import pytest
from langtrace_python_sdk.instrumentation.aws_bedrock.patch import (
    parse_vendor_and_model_name_from_model_id,
)


def test_model_id_parsing():
    model_id = "anthropic.claude-3-opus-20240229"
    vendor, model_name = parse_vendor_and_model_name_from_model_id(model_id)
    assert vendor == "anthropic"
    assert model_name == "claude-3-opus-20240229"


def test_model_id_parsing_cross_region_inference():
    model_id = "us.anthropic.claude-3-opus-20240229"
    vendor, model_name = parse_vendor_and_model_name_from_model_id(model_id)
    assert vendor == "anthropic"
    assert model_name == "claude-3-opus-20240229"


def test_model_id_parsing_arn_custom_model_inference():
    model_id = (
        "arn:aws:bedrock:us-east-1:123456789012:custom-model/amazon.my-model/abc123"
    )
    vendor, model_name = parse_vendor_and_model_name_from_model_id(model_id)
    assert vendor == "amazon"
    assert model_name == "my-model"


def test_model_id_parsing_arn_foundation_model_inference():
    model_id = "arn:aws:bedrock:us-east-1:123456789012:foundation-model/anthropic.claude-3-opus-20240229"
    vendor, model_name = parse_vendor_and_model_name_from_model_id(model_id)
    assert vendor == "anthropic"
    assert model_name == "claude-3-opus-20240229"
