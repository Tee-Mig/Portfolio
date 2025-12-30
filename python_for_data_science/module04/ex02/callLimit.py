from typing import Any, Callable


def callLimit(
        limit: int
        ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Create a decorator that limits the number of calls to a function

    Parameters:
        limit : int
            Maximum number of allowed calls for the decorated function

    Returns:
        Callable
            A decorator that wraps the target function and enforces
            the call limit
    """
    def call_limiter(function: Callable[..., Any]) -> Callable[..., Any]:
        """
        Decorator that wraps `function` and enforces the given call limit
        """
        count = 0

        def limit_function(*args: Any, **kwargs: Any) -> Any:
            """
            Call the wrapped function if the limit is not exceeded

            If the function has already been called `limit` times,
            prints an error message and does not call the function
            """
            nonlocal count
            if count >= limit:
                print(f"Error: {function} call too many times")
                return None
            count += 1
            return function(*args, **kwargs)

        return limit_function

    return call_limiter
