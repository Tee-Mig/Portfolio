import os
import numpy as np
from PIL import Image


def ft_load(path: str) -> np.ndarray:
    """
    Loads a JPEG image file and returns it as a NumPy array (RGB format).

    Parameters:
        path (str): Path to the image file. Must be a .jpg or .jpeg.

    Returns:
        np.ndarray: 3D NumPy array representing the image in RGB format.

    Raises:
        ValueError: If the file extension is not .jpg or .jpeg.
        FileNotFoundError: If the file does not exist at the given path.
        ValueError: If there is an error loading or converting the image.

    Prints:
        - The shape of the loaded image.
        - The full NumPy array representing the image.
    """
    if not (path.lower().endswith('.jpg') or path.lower().endswith('.jpeg')):
        raise ValueError("The file must be a .jpg or .jpeg")

    if not os.path.exists(path):
        raise FileNotFoundError(f"File '{path}' does not exist.")

    try:
        image = Image.open(path)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image_array = np.array(image)
    except Exception as e:
        raise ValueError(f"Error loading image: {e}")

    print(f"The shape of image is: {image_array.shape}")
    print(image_array)

    return image_array
