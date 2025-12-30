from statistics import ft_statistics
from io import StringIO
from contextlib import redirect_stdout


def subject_tests():
    ft_statistics(1, 42, 360, 11, 64,
                  toto="mean", tutu="median", tata="quartile")
    print("-----")
    ft_statistics(5, 75, 450, 18, 597, 27474, 48575, hello="std", world="var")
    print("-----")
    ft_statistics(5, 75, 450, 18, 597,
                  27474, 48575, ejfhhe="heheh", ejdjdejn="kdekem")
    print("-----")
    ft_statistics(toto="mean", tutu="median", tata="quartile")


def tests():
    GREEN = "\u2705"
    RED = "\u274C"

    def capture(*args, **kwargs) -> str:
        # Capture and return printed output of ft_statistics
        buf = StringIO()
        with redirect_stdout(buf):
            ft_statistics(*args, **kwargs)
        return buf.getvalue().strip()

    def show_result(name: str, got: str, expected: str) -> None:
        # Print comparison with checkmark and detailed outputs
        if got == expected:
            print(f"{name}: {GREEN}")
        else:
            print(f"{name}: {RED}")
            print("Expected:")
            print(expected if expected else "(no output)")
            print("Got:")
            print(got if got else "(no output)")
            print("---")

    # Expected outputs

    expected1 = (
        "mean : 95.6\n"
        "median : 42\n"
        "quartile : [11.0, 64.0]"
    )

    expected2 = (
        "std : 17982.70124086944\n"
        "var : 323377543.9183673"
    )

    expected3 = ""

    expected4 = "ERROR\nERROR\nERROR"

    # Tests

    got1 = capture(
        1, 42, 360, 11, 64,
        toto="mean", tutu="median", tata="quartile"
    )
    show_result("Test 1 (mean/median/quartile)", got1, expected1)

    got2 = capture(
        5, 75, 450, 18, 597, 27474, 48575,
        hello="std", world="var"
    )
    show_result("Test 2 (std/var)", got2, expected2)

    got3 = capture(
        5, 75, 450, 18, 597, 27474, 48575,
        ejfhhe="heheh", ejdjdejn="kdekem"
    )
    show_result("Test 3 (unknown metrics)", got3, expected3)

    got4 = capture(toto="mean", tutu="median", tata="quartile")
    show_result("Test 4 (missing args -> ERROR)", got4, expected4)


def main():
    print("Subject tests: \n")
    subject_tests()
    print("\n--------------------------------------------------------\n")
    print("More tests: \n")
    tests()


if __name__ == "__main__":
    main()
