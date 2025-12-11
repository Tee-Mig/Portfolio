import numpy as np


def check_errors_lst(lst) -> np.array:
    """
    Validates that the input is a proper 2D list (list of lists)
    with uniform row lengths.

    Parameters:
        lst (list): A list of lists representing a 2D array.

    Returns:
        np.ndarray: NumPy array converted from the validated list.

    Raises:
        TypeError: If the input is not a list or not a 2D list.
        ValueError: If the sublists do not all have the same length.
    """
    if not isinstance(lst, list):
        raise TypeError("Input must be a list")

    if not all(isinstance(row, list) for row in lst):
        raise TypeError("family must be a list of lists (2D array)")

    row_lengths = [len(row) for row in lst]
    if len(set(row_lengths)) != 1:
        raise ValueError("All rows must be of the same length")

    return np.array(lst)


def slice_me(family: list, start: int, end: int) -> list:
    """
    Slices a 2D list (matrix) between the specified start and end row indices.

    Parameters:
        family (list): A list of lists representing the matrix.
        start (int): Starting index (inclusive) for slicing rows.
        end (int): Ending index (exclusive) for slicing rows.

    Returns:
        list: A new sliced list (2D), containing the selected rows.

    Raises:
        TypeError/ValueError: If input format is
        incorrect (handled by check_errors_lst).
    """
    np_family = check_errors_lst(family)
    sliced_family = np_family[start:end]

    print(f'My shape is {np_family.shape}')
    print(f'My new shape is {sliced_family.shape}')
    return (sliced_family.tolist())
