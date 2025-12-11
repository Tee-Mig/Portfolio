from typing import Callable, Union, Any

Number = Union[int, float]


def _is_number(x: Any) -> bool:
    """
    Return True if x is an int or float (but not a bool).

    Parameters:
        x: Value to check.

    Returns:
        bool: True if x is a real number, False otherwise.
    """
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def square(x: Number) -> Number:
    """
    Return x squared.

    Parameters:
        x: Input number.

    Returns:
        Number: x * x.

    Raises:
        TypeError: If x is not an int or a float.
    """
    if not _is_number(x):
        raise TypeError("square(x): x must be an int or a float")
    return x * x


def pow(x: Number) -> Number:
    """
    Return x raised to the power of itself (x ** x).

    This function intentionally shadows the built-in pow for the exercise.

    Parameters:
        x: Input number.

    Returns:
        Number: x ** x.

    Raises:
        TypeError: If x is not an int or a float.
    """
    if not _is_number(x):
        raise TypeError("pow(x): x must be an int or a float")
    return x ** x


def outer(x: Number, function: Callable[[Number], Number]) -> object:
    """
    Return a stateful closure that repeatedly applies a function to a value.

    The returned inner function keeps an internal value. Each time it is
    called, it:
        1. Applies `function` to the current value.
        2. Updates the stored value with the result.
        3. Returns the result.

    Parameters:
        x: Initial numeric value.
        function: A callable that takes a Number and returns a Number.

    Returns:
        object: A zero-argument callable (the inner function).

    Raises:
        TypeError: If x is not numeric or function is not callable.
    """
    if not _is_number(x):
        raise TypeError("outer(x, function): x must be an int or a float")
    if not callable(function):
        raise TypeError("outer(x, function): function must be callable")

    value: Number = x

    def inner() -> float:
        """
        Apply the function to the current value, store, and return the result.

        Returns:
            float: The updated value after applying the function.
        """
        nonlocal value
        result = function(value)
        if not _is_number(result):
            raise TypeError("function must return a number")
        value = result
        return float(result)

    return inner
