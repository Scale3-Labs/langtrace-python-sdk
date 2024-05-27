import logging


def silently_fail(func):
    """
    A decorator that catches exceptions thrown by the decorated function and logs them as warnings.
    """

    logger = logging.getLogger(func.__module__)

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exception:
            logger.warning(
                "Failed to execute %s, error: %s", func.__name__, str(exception)
            )

    return wrapper
