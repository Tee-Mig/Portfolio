from give_bmi import give_bmi, apply_limit


def check_errors():
    test_cases = [
        {
            "description": "Valid input for BMI calculation",
            "input": {
                "height": [1.70, 1.80, 1.75],
                "weight": [65, 80, 75],
                "limit": 24
            },
            "expect_error": False
        },
        {
            "description": "Mismatched lengths of height and weight",
            "input": {
                "height": [1.70, 1.80],
                "weight": [65, 80, 75],
                "limit": 25
            },
            "expect_error": True
        },
        {
            "description": "Invalid type in height list",
            "input": {
                "height": [1.70, 'abc', 1.75],
                "weight": [65, 80, 75],
                "limit": 25
            },
            "expect_error": True
        },
        {
            "description": "Values must be strictly positivet",
            "input": {
                "height": [1.70, 1.60, 1.75],
                "weight": [65, 0, 75],
                "limit": 25
            },
            "expect_error": True
        },
        {
            "description": "Height is not a list",
            "input": {
                "height": (1.70, 0, 1.75),
                "weight": [65, 80, 75],
                "limit": 25
            },
            "expect_error": True
        },
        {
            "description": "Negative value in weight",
            "input": {
                "height": [1.75, 1.80],
                "weight": [70, -80],
                "limit": 24
            },
            "expect_error": True
        },
        {
            "description": "Valid BMI list input to apply_limit",
            "input": {
                "bmi": [22.5, 20, 27.8],
                "limit": 23
            },
            "expect_error": False
        },
        {
            "description": "Zero BMI value in list",
            "input": {
                "bmi": [22.5, 0, 27.8],
                "limit": 23
            },
            "expect_error": True
        },
        {
            "description": "BMI input is not a list",
            "input": {
                "bmi": (22.5, 5, 27.8),
                "limit": 23
            },
            "expect_error": True
        },
        {
            "description": "None in BMI list",
            "input": {
                "bmi": [22.5, None, 27.8],
                "limit": 23
            },
            "expect_error": True
        },
    ]

    for i, case in enumerate(test_cases, 1):
        print(f"Test {i}: {case['description']}")
        try:
            if 'height' in case["input"] and 'weight' in case["input"]:
                bmi = give_bmi(
                    case["input"]['height'],
                    case["input"]['weight']
                )
                result = apply_limit(bmi, case["input"]['limit'])
            else:
                result = apply_limit(
                    case["input"]['bmi'],
                    case["input"]['limit']
                )

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
    check_errors()
    try:
        print('\nSubject tests:\n')

        height = [2.71, 1.15]
        weight = [165.3, 38.4]
        bmi = give_bmi(height, weight)
        print(bmi, type(bmi))
        print(apply_limit(bmi, 26))
    except AssertionError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
