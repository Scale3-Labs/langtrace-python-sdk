"""
Copyright (c) 2024 Scale3 Labs
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import logging
from typing import Any, Callable, Tuple, TypeVar, cast

F = TypeVar('F', bound=Callable[..., Any])

def silently_fail(func: F) -> F:
    """
    A decorator that catches exceptions thrown by the decorated function and logs them as warnings.
    """

    logger = logging.getLogger(func.__module__)

    def wrapper(*args: Tuple[Any, ...], **kwargs: dict[str, Any]) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as exception:
            logger.warning(
                "Failed to execute %s, error: %s", func.__name__, str(exception)
            )

    return cast(F, wrapper)

