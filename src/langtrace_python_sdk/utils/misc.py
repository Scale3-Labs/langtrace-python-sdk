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


def serialize_kwargs(**kwargs):
    # Function to check if a value is serializable
    def is_serializable(value):
        try:
            json.dumps(value)
            return True
        except (TypeError, ValueError):
            return False

    # Filter out non-serializable items
    serializable_kwargs = {k: v for k, v in kwargs.items() if is_serializable(v)}

    # Convert to string representation
    return json.dumps(serializable_kwargs)


def serialize_args(*args):
    # Function to check if a value is serializable
    def is_serializable(value):
        try:
            json.dumps(value)
            return True
        except (TypeError, ValueError):
            return False

    # Filter out non-serializable items
    serializable_args = [arg for arg in args if is_serializable(arg)]

    # Convert to string representation
    return json.dumps(serializable_args)


class datetime_encoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)
