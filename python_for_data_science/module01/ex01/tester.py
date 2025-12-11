from array2D import slice_me


def test_slice_me_errors():
    test_cases = [
        {
            "description": "Valid input",
            "input": ([[1, 2], [3, 4], [5, 6]], 1, 3),
            "expect_error": False
        },
        {
            "description": "Valid input 2",
            "input": ([[1], [2], [3]], 0, 1),
            "expect_error": False
        },
        {
            "description": "Input is not a list",
            "input": ("not a list", 0, 1),
            "expect_error": True
        },
        {
            "description": "Input is not a list 2",
            "input": (([1], [2], [3]), 0, 1),
            "expect_error": True
        },
        {
            "description": "Not a 2d list",
            "input": ([1, 2, 3], 0, 1),
            "expect_error": True
        },
        {
            "description": "Rows of different lengths",
            "input": ([[1, 2], [3, 4, 5]], 0, 2),
            "expect_error": True
        },
    ]

    for i, case in enumerate(test_cases):
        print(f"Test {i+1}: {case['description']}")
        try:
            result = slice_me(*case["input"])
            if case["expect_error"]:
                print("❌ Expected an error but function ran successfully.")
            else:
                print("✅ Passed")
                print("Result:", result)
        except Exception as e:
            if case["expect_error"]:
                print(f"✅ Correctly raised an error: {e}")
            else:
                print(f"❌ Unexpected error: {e}")
        print("-" * 40)


def main():
    test_slice_me_errors()

    try:
        print('\nSubject tests:\n')

        family = [[1.80, 78.4], [2.15, 102.7], [2.10, 98.5], [1.88, 75.2]]

        print(slice_me(family, 0, 2))
        print(slice_me(family, 1, -2))
    except AssertionError as e:
        print(f"Error: {e}")
    return 0


if __name__ == "__main__":
    main()
