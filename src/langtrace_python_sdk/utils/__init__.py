from openai import NOT_GIVEN
from .sdk_version_checker import SDKVersionChecker


def set_span_attribute(span, name, value):
    if value is not None:
        if value != "" or value != NOT_GIVEN:
            span.set_attribute(name, value)
    return


def check_if_sdk_is_outdated():
    SDKVersionChecker().check()
    return
