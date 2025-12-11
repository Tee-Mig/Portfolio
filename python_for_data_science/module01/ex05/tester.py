import numpy as np
from pimp_image import ft_invert, ft_red, ft_green, ft_blue, ft_grey
from load_image import ft_load
import matplotlib.pyplot as plt


def test_color_filters_errors():
    test_cases = [
        {
            "description": "Valid RGB array (uint8)",
            "input": np.ones((10, 10, 3), dtype=np.uint8) * 100,
            "expect_error": False
        },
        {
            "description": "Grayscale image (2D array)",
            "input": np.ones((10, 10), dtype=np.uint8) * 100,
            "expect_error": True
        },
        {
            "description": "RGB image but wrong type (float)",
            "input": np.ones((10, 10, 3), dtype=float),
            "expect_error": False
        },
        {
            "description": "RGB image but wrong shape (extra channel)",
            "input": np.ones((10, 10, 4), dtype=np.uint8),
            "expect_error": True
        },
        {
            "description": "1D array instead of image",
            "input": np.array([1, 2, 3]),
            "expect_error": True
        },
        {
            "description": "None as input",
            "input": None,
            "expect_error": True
        },
    ]

    functions = [ft_invert, ft_red, ft_green, ft_blue, ft_grey]

    for i, case in enumerate(test_cases):
        print(f"Test {i + 1}: {case['description']}")
        for func in functions:
            print(f"  Function: {func.__name__}")
            try:
                func(case["input"])
                if case["expect_error"]:
                    print("    ❌ Expected an error but function ")
                    print("ran successfully.")
                else:
                    print("    ✅ Passed")
            except Exception as e:
                if case["expect_error"]:
                    print(f"    ✅ Correctly raised an error: {e}")
                else:
                    print(f"    ❌ Unexpected error: {e}")
        print("-" * 50)


def main():
    test_color_filters_errors()

    try:
        print('\nSubject tests\n')

        array = ft_load("landscape.jpg")

        plt.imshow(array)
        plt.title("Original Image")
        plt.axis("off")
        plt.show()

        ft_invert(array)
        ft_red(array)
        ft_green(array)
        ft_blue(array)
        ft_grey(array)

        print(ft_invert.__doc__)
    except AssertionError as e:
        print(f'Error: {e}')
    return 0


if __name__ == "__main__":
    main()
