

from __future__ import annotations

import functools
from typing import Any, Callable, Type

from tenacity import (
    RetryError,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log,
)

from config.logging_config import get_logger

logger = get_logger(__name__)


def with_retry(
    max_attempts: int = 3,
    min_wait: float = 1.0,
    max_wait: float = 30.0,
    retry_on: tuple[Type[Exception], ...] = (Exception,),
) -> Callable:
    """
    Decorator for retrying functions with exponential backoff.

    Parameters
    ----------
    max_attempts : int
        Maximum number of retry attempts.
    min_wait : float
        Minimum wait time between retries (seconds).
    max_wait : float
        Maximum wait time between retries (seconds).
    retry_on : tuple
        Exception types that trigger a retry.
    """

    def decorator(func: Callable) -> Callable:
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
            retry=retry_if_exception_type(retry_on),
            reraise=True,
        )
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        return wrapper

    return decorator


def retry_api_call(func: Callable, *args: Any, max_attempts: int = 3, **kwargs: Any) -> Any:
    """
    Retry an API call with exponential backoff (functional style).

    Parameters
    ----------
    func : Callable
        Function to call.
    max_attempts : int
        Maximum attempts.

    Returns
    -------
    Any
        Result of the function call.

    Raises
    ------
    Exception
        The last exception if all retries fail.
    """
    last_exc: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            last_exc = exc
            if attempt < max_attempts:
                import time

                wait_time = min(2**attempt, 30)
                logger.warning(
                    "retry_attempt",
                    function=func.__name__,
                    attempt=attempt,
                    max_attempts=max_attempts,
                    wait_time=wait_time,
                    error=str(exc),
                )
                time.sleep(wait_time)

    raise last_exc  
