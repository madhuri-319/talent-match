"""
Tracer - Distributed tracing and performance monitoring.
"""

import logging
import time
from functools import wraps
from typing import Any, Callable, Dict

logger = logging.getLogger(__name__)


class Tracer:
    """Simple tracer for monitoring function calls and performance."""

    def __init__(self):
        """Initialize tracer."""
        self.traces: Dict[str, list] = {}

    def trace_function(self, func: Callable) -> Callable:
        """
        Decorator to trace function execution.

        Args:
            func: Function to trace

        Returns:
            Wrapped function with tracing
        """

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            func_name = f"{func.__module__}.{func.__name__}"

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(
                    f"Function {func_name} completed in {duration:.2f}s"
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"Function {func_name} failed after {duration:.2f}s: {str(e)}"
                )
                raise

        return wrapper


# Global tracer instance
tracer = Tracer()
