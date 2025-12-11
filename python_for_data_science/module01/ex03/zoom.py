import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from load_image import ft_load


def zoom(path: str, crop_size=400, shift_x=140, shift_y=-90):
    """
    Loads an RGB image, converts it to grayscale, crops a zoomed region, and
    displays boththe original and the zoomed grayscale image side by side
    using matplotlib.

    Parameters:
        path (str): Path to the input image (must be .jpg or .jpeg).
        crop_size (int): Size of the square crop to extract from the
            grayscale image. Default is 400.
        shift_x (int): Horizontal shift to apply to the crop
            position. Default is 140.
        shift_y (int): Vertical shift to apply to the crop
            position. Default is -90.

    Returns:
        None

    Raises:
        ValueError/FileNotFoundError: If the image path is
            invalid (handled by ft_load).
        Prints error and returns if the loaded image is not RGB (3 channels).

    Displays:
        - The original RGB image with grid ticks.
        - The cropped zoomed grayscale version of the image.
    """
    img_rgb = ft_load(path)

    if len(img_rgb.shape) != 3 or img_rgb.shape[2] != 3:
        raise ValueError("Error: Expected an RGB image with 3 channels.")

    height, width = img_rgb.shape[0:2]

    img_gray = Image.fromarray(img_rgb).convert("L")

    left = min((width - crop_size) // 2 + shift_x, width - crop_size)
    top = (height - crop_size) // 2 + shift_y
    right = left + crop_size
    bottom = top + crop_size

    zoom_crop = img_gray.crop((left, top, right, bottom))
    zoom_array = np.array(zoom_crop)

    zoom_array_3d = np.expand_dims(zoom_array, axis=2)

    print(
        f"New shape after slicing: {zoom_array_3d.shape} "
        f"or {zoom_array.shape}"
    )
    print(zoom_array_3d)

    axes = plt.subplots(1, 2, figsize=(12, 6))[1]

    axes[0].imshow(img_rgb)
    axes[0].set_title("Original Image")
    axes[0].set_xticks(np.arange(0, img_rgb.shape[1], 200))
    axes[0].set_yticks(np.arange(0, img_rgb.shape[0], 200))
    axes[0].set_xlabel("X axis (pixels)")
    axes[0].set_ylabel("Y axis (pixels)")

    axes[1].imshow(
        zoom_array,
        cmap="gray",
        extent=[0, crop_size, crop_size, 0]
    )
    axes[1].set_title("Zoomed Grayscale View")
    axes[1].set_xticks(np.arange(0, zoom_array.shape[1], 50))
    axes[1].set_yticks(np.arange(0, zoom_array.shape[0], 50))
    axes[1].set_xlabel("X axis (pixels)")
    axes[1].set_ylabel("Y axis (pixels)")

    plt.tight_layout()
    plt.show()
