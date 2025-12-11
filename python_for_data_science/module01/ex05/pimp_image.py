import numpy as np
import matplotlib.pyplot as plt


def validate_rgb_image(array) -> None:
    """
    Validates that the input is a NumPy RGB image with shape (H, W, 3).
    Raises a ValueError if the input is invalid.

    Args:
        array (np.ndarray): Image to validate.

    Raises:
        ValueError: If array is not a valid RGB image.
    """
    import numpy as np

    if (
        not isinstance(array, np.ndarray)
        or array.ndim != 3
        or array.shape[2] != 3
    ):
        raise ValueError("Input must be an RGB image with shape (H, W, 3).")


def ft_invert(array) -> np.ndarray:
    """
    Apply a color inversion filter to the input RGB image.
    Each pixel is transformed as: new_value = 255 - original_value.
    Allowed operations: =, +, -, *.

    Args:
        array (np.ndarray): Input RGB image of shape (H, W, 3).

    Returns:
        np.ndarray: Color-inverted image with the same shape.
    """
    validate_rgb_image(array)
    inverted = array * 0 + 255 - array
    plt.imshow(inverted)
    plt.title("Inverted Image")
    plt.axis("off")
    plt.show()
    return inverted


def ft_red(array) -> np.ndarray:
    """
    Apply a red filter by keeping only the red channel and zeroing others.
    Allowed operations: =, *.

    Args:
        array (np.ndarray): Input RGB image of shape (H, W, 3).

    Returns:
        np.ndarray: Image showing only red tones.
    """
    validate_rgb_image(array)
    red_image = array * 1
    red_image[:, :, 1] = red_image[:, :, 1] * 0
    red_image[:, :, 2] = red_image[:, :, 2] * 0
    plt.imshow(red_image)
    plt.title("Red Filter")
    plt.axis("off")
    plt.show()
    return red_image


def ft_green(array) -> np.ndarray:
    """
    Apply a green filter by keeping only the green channel and zeroing others.
    Allowed operations: =, -.

    Args:
        array (np.ndarray): Input RGB image of shape (H, W, 3).

    Returns:
        np.ndarray: Image showing only green tones.
    """
    validate_rgb_image(array)
    green_image = array - array
    green_image[:, :, 1] = array[:, :, 1]
    plt.imshow(green_image)
    plt.title("Green Filter")
    plt.axis("off")
    plt.show()
    return green_image


def ft_blue(array) -> np.ndarray:
    """
    Apply a blue filter by keeping only the blue channel and zeroing others.
    Allowed operations: =.

    Args:
        array (np.ndarray): Input RGB image of shape (H, W, 3).

    Returns:
        np.ndarray: Image showing only blue tones.
    """
    validate_rgb_image(array)
    blue_image = array.copy()
    blue_image[:, :, 0] = 0
    blue_image[:, :, 1] = 0
    plt.imshow(blue_image)
    plt.title("Blue Filter")
    plt.axis("off")
    plt.show()
    return blue_image


def ft_grey(array) -> np.ndarray:
    """
    Convert the RGB image to grayscale using the average of the 3 channels.
    Allowed operations: =, /.

    Args:
        array (np.ndarray): Input RGB image of shape (H, W, 3).

    Returns:
        np.ndarray: Grayscale image with same shape (H, W, 3),
                    where all channels are equal.
    """
    validate_rgb_image(array)
    grey = (
        array[:, :, 0] / 3 +
        array[:, :, 1] / 3 +
        array[:, :, 2] / 3
    )
    grey_image = np.zeros_like(array)
    grey_image[:, :, 0] = grey
    grey_image[:, :, 1] = grey
    grey_image[:, :, 2] = grey
    plt.imshow(grey_image.astype(np.uint8))
    plt.title("Grayscale Image")
    plt.axis("off")
    plt.show()
    return grey_image.astype(np.uint8)
