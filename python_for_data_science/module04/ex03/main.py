from new_student import Student


def subject_tests() -> None:
    student = Student(name="Edward", surname="agle")
    print(student)


def tests() -> None:
    # Test 1: automatic fields (active, login, id)
    try:
        student = Student(name="Edward", surname="agle")
        ok_login = student.login == "Eagle"
        ok_active = student.active is True
        ok_id = isinstance(student.id, str) and len(student.id) == 15 \
            and student.id.islower()

        if ok_login and ok_active and ok_id:
            print(
                "\u2705 Automatic fields OK "
                f"(login={student.login!r}, active={student.active}, "
                f"id={student.id!r})",
            )
        else:
            print(
                "\u274C Automatic fields incorrect "
                f"(login={student.login!r}, active={student.active}, "
                f"id={student.id!r})",
            )
    except Exception as exc:
        print(f"\u274C Creating a valid student raised an exception: {exc!r}")

    # Test 2: login must not be initializable
    try:
        Student(name="Edward", surname="agle", login="Foo")
        print(
            "\u274C Passing login in constructor did not raise TypeError",
        )
    except TypeError:
        print("\u2705 Passing login in constructor raises TypeError")
    except Exception as exc:
        print(
            "\u274C Passing login raised the wrong exception type: "
            f"{exc!r}",
        )

    # Test 3: id must not be initializable
    try:
        Student(name="Edward", surname="agle", id="toto")
        print("\u274C Passing id in constructor did not raise TypeError")
    except TypeError:
        print("\u2705 Passing id in constructor raises TypeError")
    except Exception as exc:
        print(
            "\u274C Passing id raised the wrong exception type: "
            f"{exc!r}",
        )

    # Test 4: different students should have different ids
    try:
        s1 = Student(name="Alice", surname="foo")
        s2 = Student(name="Bob", surname="bar")
        if s1.id != s2.id:
            print(
                "\u2705 Different students have different ids "
                f"({s1.id!r} vs {s2.id!r})",
            )
        else:
            print(
                "\u274C Two students share the same id "
                f"({s1.id!r}), which is highly unlikely.",
            )
    except Exception as exc:
        print(f"\u274C Error while creating multiple students: {exc!r}")


def main() -> None:
    print("Subject tests: \n")
    subject_tests()
    print("\n--------------------------------------------------------\n")
    print("More tests: \n")
    tests()


if __name__ == "__main__":
    main()
