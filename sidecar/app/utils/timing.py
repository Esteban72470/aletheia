"""Timing utilities."""

import time
from contextlib import contextmanager
from functools import wraps
from typing import Callable, Optional

from app.logging import get_logger

logger = get_logger(__name__)


class Timer:
    """Simple timer for measuring durations."""

    def __init__(self):
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

    def start(self):
        """Start the timer."""
        self.start_time = time.perf_counter()
        self.end_time = None

    def stop(self) -> float:
        """
        Stop the timer.

        Returns:
            Elapsed time in seconds
        """
        self.end_time = time.perf_counter()
        return self.elapsed

    @property
    def elapsed(self) -> float:
        """Get elapsed time in seconds."""
        if self.start_time is None:
            return 0.0
        end = self.end_time or time.perf_counter()
        return end - self.start_time

    @property
    def elapsed_ms(self) -> int:
        """Get elapsed time in milliseconds."""
        return int(self.elapsed * 1000)


@contextmanager
def timer(name: str = "operation", log: bool = True):
    """
    Context manager for timing operations.

    Args:
        name: Operation name for logging
        log: Whether to log the duration

    Yields:
        Timer instance
    """
    t = Timer()
    t.start()
    try:
        yield t
    finally:
        t.stop()
        if log:
            logger.debug(f"{name} took {t.elapsed_ms}ms")


def timed(name: Optional[str] = None):
    """
    Decorator for timing function execution.

    Args:
        name: Optional name (defaults to function name)

    Returns:
        Decorated function
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            op_name = name or func.__name__
            with timer(op_name):
                return func(*args, **kwargs)

        return wrapper

    return decorator
