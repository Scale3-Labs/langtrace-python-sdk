from typing import TypedDict


class LangTraceEvaluation:
    # Define the class based on your needs
    pass


class LangTraceApiError(Exception):
    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.status_code = status_code


class EvaluationAPIData(TypedDict):
    userId: str
    userScore: int
    traceId: str
    spanId: str
