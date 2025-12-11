from load_image import ft_load


def test_ft_load_errors():
    test_cases = [
        {
            "description": "Valid jpg file",
            "input": "landscape.jpg",
            "expect_error": False
        },
        {
            "description": "JPEG with uppercase extension",
            "input": "animal.JPEG",
            "expect_error": True
        },
        {
            "description": "File with unsupported extension",
            "input": "animal.png",
            "expect_error": True
        },
        {
            "description": "File does not exist",
            "input": "non_existent.jpg",
            "expect_error": True
        },
        {
            "description": "File is not an image (e.g., .txt)",
            "input": "not_an_image.txt",
            "expect_error": True
        },
    ]

    for i, case in enumerate(test_cases):
        print(f"Test {i+1}: {case['description']}")
        try:
            result = ft_load(case["input"])
            if case["expect_error"]:
                print("❌ Expected an error but function ran successfully.")
            else:
                print("✅ Passed")
                print("Result shape:", result.shape)
        except Exception as e:
            if case["expect_error"]:
                print(f"✅ Correctly raised an error: {e}")
            else:
                print(f"❌ Unexpected error: {e}")
        print("-" * 40)


def main():
    test_ft_load_errors()

    try:
        print('\nSubject tests:\n')

        print('jpg file:')
        print(ft_load("landscape.jpg"))
        print('\njpeg file:')
        print(ft_load("animal.jpeg"))
    except AssertionError as e:
        print(f'Error: {e}')
    return 0


if __name__ == "__main__":
    main()
