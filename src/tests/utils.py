from unittest.mock import MagicMock, patch
import json
   
def common_setup(data, method_to_mock=None):
    if method_to_mock:
        service_mock = patch(method_to_mock)
        mock_method = service_mock.start()
        mock_method.return_value = json.dumps(data)
    else:
        service_mock = None
        mock_method = None

    tracer = MagicMock()
    span = MagicMock()

    context_manager_mock = MagicMock()
    context_manager_mock.__enter__.return_value = span
    tracer.start_as_current_span.return_value = context_manager_mock

    return service_mock, tracer, span