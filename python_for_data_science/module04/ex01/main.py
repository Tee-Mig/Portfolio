from in_out import outer
from in_out import square
from in_out import pow


def subject_tests():
    my_counter = outer(3, square)
    print(my_counter())
    print(my_counter())
    print(my_counter())
    print("---")
    another_counter = outer(1.5, pow)
    print(another_counter())
    print(another_counter())
    print(another_counter())


def tests():
    GREEN = "\u2705"
    RED = "\u274C"

    def check(test_name: str, got: float, expected: float) -> None:
        # Print success/failure for a single numerical test
        if abs(got - expected) < 1e-12:
            print(f"{test_name}: {GREEN}  (got {got})")
        else:
            print(
                f"{test_name}: {RED}  (got {got}, expected {expected})"
            )

    print("=== Test 1: outer(3, square) ===")
    counter = outer(3, square)

    expected_values_1 = [9, 81, 6561]
    for i, expected in enumerate(expected_values_1, start=1):
        got = counter()
        check(f"square call {i}", got, expected)

    print("\n=== Test 2: outer(1.5, pow) ===")
    counter2 = outer(1.5, pow)

    expected_values_2 = [
        1.8371173070873836,
        3.056683336818703,
        30.42684786675409,
    ]

    for i, expected in enumerate(expected_values_2, start=1):
        got = counter2()
        check(f"pow call {i}", got, expected)

    print("\n=== Error tests ===")

    # Test invalid x
    try:
        outer("hello", square)
        print("invalid x test: " + RED)
    except TypeError:
        print("invalid x test: " + GREEN)

    # Test non-callable
    try:
        outer(3, "not a function")
        print("invalid function test: " + RED)
    except TypeError:
        print("invalid function test: " + GREEN)

    # Test function returning invalid output
    def bad_function(x):
        return "oops"

    try:
        bad = outer(3, bad_function)
        bad()
        print("bad function return test: " + RED)
    except TypeError:
        print("bad function return test: " + GREEN)


def main():
    print("Subject tests: \n")
    subject_tests()
    print("\n--------------------------------------------------------\n")
    print("More tests: \n")
    tests()


if __name__ == "__main__":
    main()
