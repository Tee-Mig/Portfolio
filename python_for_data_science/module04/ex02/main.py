from callLimit import callLimit
from io import StringIO
from contextlib import redirect_stdout


@callLimit(3)
def f():
    print("f()")


@callLimit(1)
def g():
    print("g()")


def subject_tests():
    for i in range(3):
        f()
        g()


def _mark(ok: bool) -> str:
    return "\u2705" if ok else "\u274C"


def _capture_output(func, *args, **kwargs) -> str:
    buf = StringIO()
    with redirect_stdout(buf):
        func(*args, **kwargs)
    return buf.getvalue().strip()


def tests() -> None:
    # ---------- Test 1: limit = 1 ----------
    @callLimit(1)
    def h() -> None:
        print("h()")

    out1 = _capture_output(h)
    first_ok = out1 == "h()"
    print(f"{_mark(first_ok)} First call ok (prints h())")

    out2 = _capture_output(h)
    second_ok = (
        "Error: <function" in out2
        and "h" in out2
        and "call too many times" in out2
        and "h()" not in out2
    )
    print(f"{_mark(second_ok)} Second call shows correct error")

    # ---------- Test 2: limit = 0 ----------
    @callLimit(0)
    def k() -> None:
        print("k()")

    out0_1 = _capture_output(k)
    limit0_ok = (
        "Error: <function" in out0_1
        and "call too many times" in out0_1
        and "k()" not in out0_1
    )
    print(f"{_mark(limit0_ok)} Function blocked immediately when limit=0")

    out0_2 = _capture_output(k)
    multi_error_ok = (
        "Error: <function" in out0_2
        and "call too many times" in out0_2
        and "k()" not in out0_2
    )
    print(f"{_mark(multi_error_ok)} ", end="")
    print("Multiple calls after limit give consistent errors")


def main():
    print("Subject tests: \n")
    subject_tests()
    print("\n--------------------------------------------------------\n")
    print("More tests: \n")
    tests()


if __name__ == "__main__":
    main()
