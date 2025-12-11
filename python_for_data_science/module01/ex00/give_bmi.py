import numpy as np


def check_errors_lst(lst):
    """
    Validates the input list to ensure it contains only
        positive integers or floats.

    Parameters:
        lst (list): List of numerical values to validate.

    Returns:
        np.ndarray: NumPy array of the validated list.

    Raises:
        AssertionError: If lst is not a list, contains non-numeric values,
                        or contains non-positive values.
    """
    assert isinstance(lst, list), 'Variable is not a list'
    assert all(isinstance(x, (int, float)) for x in lst), \
        'List must contain only int or float'
    assert all(x > 0 for x in lst), 'Values must be strictly positive'
    return np.array(lst)


def give_bmi(height: list[int | float],
             weight: list[int | float]) -> list[int | float]:
    """
        Compute the body mass index(bmi) and return the result

        Parameters:
            height: list[int | float]: height of the person(s)
            weight: list[int | float]: weight of the person(s)

        Returns:
            list[int | float]: body mass index(bmi) of the person(s)
    """

    np_height = check_errors_lst(height)
    np_weight = check_errors_lst(weight)
    assert np_height.shape == np_weight.shape, (
        f"Input lists must have the same length, "
        f"got heights: {np_height.shape[0]} "
        f"and weights: {np_weight.shape[0]}"
    )

    return ((np_weight / (np_height ** 2)).tolist())


def apply_limit(bmi: list[int | float], limit: int) -> list[bool]:
    """
        Check if body mass index(bmi) is greater than the limit

        Parameters:
            bmi: list[int | float]: body mass index(bmi) of the person(s)
            limit: int: limit for body mass index(bmi)

        Returns:
            list[bool]: if the body mass index(bmi) is greater than the limit
    """

    np_bmi = check_errors_lst(bmi)
    return ((np_bmi > limit).tolist())
