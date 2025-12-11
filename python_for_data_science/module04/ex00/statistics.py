from typing import Any, Iterable, List
import math


def _is_number(x: Any) -> bool:
    """
    Return True if x is a real number (int or float), excluding booleans.

    Parameters:
        x (Any): The value to test.

    Returns:
        bool: True if x is int/float and not a bool, else False.
    """
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _to_list_numbers(args: Iterable[Any]) -> List[float]:
    """
    Convert *args to a list of numbers if valid.

    Rules:
    - If the iterable is empty → return []
    - If ANY element is not a valid number → return []

    Parameters:
        args (Iterable[Any]): Input values.

    Returns:
        List[float]: A list of numbers, or [] on invalid input.
    """
    vals = list(args)
    if not vals or not all(_is_number(v) for v in vals):
        return []
    return vals


def _mean(xs: List[float]) -> float:
    """
    Compute the arithmetic mean of a non-empty list of numbers.

    Parameters:
        xs (List[float]): Input list.

    Returns:
        float: The mean value.
    """
    return sum(xs) / len(xs)


def _median(xs: List[float]) -> float:
    """
    Compute the median of a non-empty list of numbers.

    Parameters:
        xs (List[float]): Input list.

    Returns:
        float: The median value.
    """
    s = sorted(xs)
    n = len(s)
    mid = n // 2
    if n % 2:
        return float(s[mid])
    return (s[mid - 1] + s[mid]) / 2.0


def _quantile(xs: List[float], q: float) -> float:
    """
    Compute a quantile of a list using linear interpolation.

    Parameters:
        xs (List[float]): Input list.
        q (float): Quantile in [0,1], e.g., 0.25 or 0.75.

    Returns:
        float: The interpolated quantile value.
    """
    s = sorted(xs)
    n = len(s)
    if n == 1:
        return float(s[0])

    pos = (n - 1) * q
    lo = math.floor(pos)
    hi = math.ceil(pos)

    if lo == hi:
        return float(s[lo])

    return float(s[lo] + (s[hi] - s[lo]) * (pos - lo))


def _variance(xs: List[float]) -> float:
    """
    Compute the population variance of a non-empty list.

    Parameters:
        xs (List[float]): Input list.

    Returns:
        float: The population variance (division by n).
    """
    mu = _mean(xs)
    return sum((x - mu) ** 2 for x in xs) / len(xs)


def _print_right_number_type(x: float) -> str:
    """
    Format numbers for display:
    - If x is an integer (e.g., 42.0), return "42"
    - Otherwise return a float string.

    Parameters:
        x (float): The number to display.

    Returns:
        str: The formatted number as a string.
    """
    return str(int(x)) if float(x).is_integer() else repr(float(x))


def ft_statistics(*args: Any, **kwargs: Any) -> None:
    """
    Compute and print statistics based on the metrics requested in **kwargs.

    Accepted metric values:
        "mean", "median", "quartile", "std", "var"

    Behavior:
    - If *args is empty or contains
        a non-number → print "ERROR" for each metric.
    - Unknown metrics are ignored silently.
    - Results are printed in the order of kwargs.values().

    Parameters:
        **args (Any): Numerical values to process.
        **kwargs (Any): Metrics to compute (values, not keys).

    Returns:
        None
    """
    data = _to_list_numbers(args)

    for metric in kwargs.values():
        if not data:
            print("ERROR")
            continue

        if metric == "mean":
            print(f"mean : {_print_right_number_type(_mean(data))}")

        elif metric == "median":
            print(f"median : {_print_right_number_type(_median(data))}")

        elif metric == "quartile":
            q1 = _quantile(data, 0.25)
            q3 = _quantile(data, 0.75)
            print(f"quartile : [{repr(float(q1))}, {repr(float(q3))}]")

        elif metric == "std":
            std = math.sqrt(_variance(data))
            print(f"std : {repr(float(std))}")

        elif metric == "var":
            print(f"var : {repr(float(_variance(data)))}")

        else:
            pass
