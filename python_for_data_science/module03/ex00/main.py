from S1E9 import Character, Stark

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"
CHECK = "✅"
CROSS = "❌"


def run_test(description, func):
    """Exécute un test et affiche le résultat avec un effet visuel."""
    try:
        func()
        print(f"{GREEN}{CHECK} {description}{RESET}")
    except AssertionError as e:
        print(f"{RED}{CROSS} {description} -> {e}{RESET}")
    except Exception as e:
        print(
            f"{RED}{CROSS} {description} -> "
            f"Exception inattendue: {e}{RESET}"
        )


def test_stark_is_alive_default():
    ned = Stark("Ned")
    assert ned.is_alive is True, (
        "is_alive devrait être True par défaut"
    )


def test_stark_die_method():
    ned = Stark("Ned")
    ned.die()
    assert ned.is_alive is False, (
        "Après die(), is_alive devrait être False"
    )


def test_docstrings_exist():
    assert isinstance(Stark.__doc__, str) and Stark.__doc__, (
        "Docstring de Stark manquante"
    )
    assert (
        isinstance(Stark.__init__.__doc__, str)
        and Stark.__init__.__doc__
    ), "Docstring de __init__ manquante"
    assert isinstance(Stark.die.__doc__, str) and Stark.die.__doc__, (
        "Docstring de die() manquante"
    )


def test_character_is_abstract():
    try:
        _ = Character("Hodor")  # type: ignore[abstract]
        assert False, (
            "Character devrait être abstraite "
            "et non instanciable"
        )
    except TypeError:
        pass


def extra_tests():
    print("\n=== Lancement des tests supplémentaires ex00 ===")
    run_test("Stark.is_alive est True par défaut", test_stark_is_alive_default)
    run_test("Stark.die() change is_alive en False", test_stark_die_method)
    run_test("Les docstrings existent", test_docstrings_exist)
    run_test(
        "Character est abstraite (non instanciable)",
        test_character_is_abstract,
    )
    print("=== Fin des tests ===")


def subject_tests():
    print("=== Sujet ex00 ===")
    ned = Stark("Ned")
    print(ned.__dict__)
    print(ned.is_alive)
    ned.die()
    print(ned.is_alive)
    print(ned.__doc__)
    print(ned.__init__.__doc__)
    print(ned.die.__doc__)
    print("---")
    lyanna = Stark("Lyanna", False)
    print(lyanna.__dict__)
    print("=== Fin des tests sujet ===")


def main():
    subject_tests()
    extra_tests()
    return 0


if __name__ == "__main__":
    main()
