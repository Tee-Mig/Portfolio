import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from load_image import ft_load


def manual_transpose(matrix):
    """
    Manually transposes a 2D NumPy array.

    Parameters:
        matrix (np.ndarray): 2D NumPy array to transpose.

    Returns:
        np.ndarray: Transposed version of the input matrix.
    """
    rows, cols = matrix.shape
    transposed = np.zeros((cols, rows), dtype=matrix.dtype)
    for i in range(rows):
        for j in range(cols):
            transposed[j, i] = matrix[i, j]
    return transposed


def rotate(path: str, crop_size=400, shift_x=140, shift_y=-90):
    """
    Loads an RGB image, converts it to grayscale, crops a region,
        transposes it manually, and displays the original image
        alongside the transposed grayscale crop.

    Parameters:
        path (str): Path to the image file (must be a .jpg/.jpeg).
        crop_size (int): Size of the square crop to extract. Default is 400.
        shift_x (int): Horizontal offset from center crop. Default is 140.
        shift_y (int): Vertical offset from center crop. Default is -90.

    Returns:
        None

    Displays:
        - The original RGB image.
        - The manually transposed grayscale zoom of the selected region.
        - Prints the shapes and array values for debugging.
    """
    img_rgb = ft_load(path)

    if len(img_rgb.shape) != 3 or img_rgb.shape[2] != 3:
        raise ValueError("Error: Expected an RGB image with 3 channels.")

    height, width = img_rgb.shape[0:2]

    image_gray = Image.fromarray(img_rgb).convert("L")

    left = min((width - crop_size) // 2 + shift_x, width - crop_size)
    top = (height - crop_size) // 2 + shift_y
    right = left + crop_size
    bottom = top + crop_size

    zoom_crop = image_gray.crop((left, top, right, bottom))
    zoom_array = np.array(zoom_crop)

    transposed_array = manual_transpose(zoom_array)
    print("New shape after Transpose:", transposed_array.shape)
    print(transposed_array)

    axes = plt.subplots(1, 2, figsize=(12, 6))[1]

    axes[0].imshow(img_rgb)
    axes[0].set_title("Original Image")
    axes[0].set_xticks(np.arange(0, img_rgb.shape[1], 200))
    axes[0].set_yticks(np.arange(0, img_rgb.shape[0], 200))
    axes[0].set_xlabel("X axis (pixels)")
    axes[0].set_ylabel("Y axis (pixels)")

    axes[1].imshow(
        transposed_array,
        cmap="gray",
        extent=[0, crop_size, crop_size, 0]
        )
    axes[1].set_title("Zoomed Grayscale View")
    axes[1].set_xticks(np.arange(0, transposed_array.shape[1], 50))
    axes[1].set_yticks(np.arange(0, transposed_array.shape[0], 50))
    axes[1].set_xlabel("X axis (pixels)")
    axes[1].set_ylabel("Y axis (pixels)")

    plt.tight_layout()
    plt.show()
