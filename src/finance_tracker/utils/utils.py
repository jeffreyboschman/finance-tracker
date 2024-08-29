import asyncio
import functools
import logging
import time
from typing import Any, Callable, Coroutine

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


def timing_decorator(func: Callable[..., Any]) -> Callable[..., Any]:
    """A decorator that logs the execution time of the function it wraps,
    preserving its sync or async nature.

    This decorator can be applied to both synchronous and asynchronous functions.
    It measures the execution time of the function and logs it using the Python
    logging module. The execution time is logged at the INFO level.

    Args:
        func: The function to be wrapped by the decorator.

    Returns:
        The wrapped function, which logs its execution time when called.
    """

    @functools.wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()

        if args and hasattr(args[0], "__class__"):
            class_name = args[0].__class__.__name__
            _logger.info(
                "%s.%s executed in %.4f seconds",
                class_name,
                func.__name__,
                end_time - start_time,
            )
        else:
            _logger.info(
                "%s executed in %.4f seconds", func.__name__, end_time - start_time
            )
        return result

    @functools.wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Coroutine:
        start_time = time.perf_counter()
        result = await func(*args, **kwargs)
        end_time = time.perf_counter()

        if args and hasattr(args[0], "__class__"):
            class_name = args[0].__class__.__name__
            _logger.info(
                "%s.%s executed in %.4f seconds",
                class_name,
                func.__name__,
                end_time - start_time,
            )
        else:
            _logger.info(
                "%s executed in %.4f seconds", func.__name__, end_time - start_time
            )
        return result

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper
