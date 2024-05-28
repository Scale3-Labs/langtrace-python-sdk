from datetime import datetime
import json


def extract_input_params(args, kwargs):
    extracted_params = {}
    for key, value in kwargs.items():
        if hasattr(value, "__dict__"):
            extracted_params[key] = json.dumps(vars(value))
        else:
            extracted_params[key] = value
    for i, value in enumerate(args):
        if hasattr(value, "__dict__"):
            extracted_params[f"arg{i}"] = json.dumps(vars(value))
        else:
            extracted_params[f"arg{i}"] = value
    # Remove None values
    return {k: v for k, v in extracted_params.items() if v is not None}


def to_iso_format(value):
    return (
        None
        if value is None
        else (
            value.isoformat(timespec="microseconds") + "Z"
            if isinstance(value, datetime)
            else None
        )
    )
