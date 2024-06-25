# Description

Please include a summary of the changes and the related issue to help is review the PR better and faster.

# Checklist for adding new integration:

- [ ] Defined `APIS` in constants [folder](../src/langtrace_python_sdk/constants/instrumentation/).
- [ ] Updated `SERVICE_PROVIDERS` in [common.py](../src/langtrace_python_sdk/constants/instrumentation/common.py)
- [ ] Created a folder under [instrumentation](../src/langtrace_python_sdk/instrumentation/) with the name of the integration with atleast `patch.py` and `instrumentation.py` files.
- [ ] Added instrumentation in `all_instrumentations` in [langtrace.py](../src/langtrace_python_sdk/langtrace.py) and to the `InstrumentationType` in [types.py](../src/langtrace_python_sdk/types/__init__.py) files.
- [ ] Added examples for the new integration in the [examples](../src/langtrace_python_sdk/examples/) folder.
- [ ] Updated [pyproject.toml](../pyproject.toml) to install new dependencies
- [ ] Updated the [README.md](../README.md) of [langtrace-python-sdk](https://github.com/Scale3-Labs/langtrace-python-sdk) to include the new integration in the supported integrations table.
- [ ] Updated the [README.md](https://github.com/Scale3-Labs/langtrace?tab=readme-ov-file#supported-integrations) of Langtrace's [repository](https://github.com/Scale3-Labs/langtrace) to include the new integration in the supported integrations table.
- [ ] Added new integration page to supported integrations in [Langtrace Docs](https://github.com/Scale3-Labs/langtrace-docs)
