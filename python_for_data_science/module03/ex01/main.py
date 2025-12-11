from S1E7 import Baratheon, Lannister

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"
CHECK = "✅"
CROSS = "❌"


def run_test(description, func):
    """Exécute un test et affiche le résultat avec effet visuel."""
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


def test_baratheon_init():
    robert = Baratheon("Robert")
    assert robert.first_name == "Robert", "first_name incorrect"
    assert robert.family_name == "Baratheon", "family_name incorrect"
    assert robert.eyes == "brown", "eyes par défaut incorrect"
    assert robert.hairs == "dark", "hairs par défaut incorrect"


def test_lannister_init():
    cersei = Lannister("Cersei")
    assert cersei.first_name == "Cersei", "first_name incorrect"
    assert cersei.family_name == "Lannister", "family_name incorrect"
    assert cersei.eyes == "blue", "eyes par défaut incorrect"
    assert cersei.hairs == "light", "hairs par défaut incorrect"


def test_die_method():
    robert = Baratheon("Robert")
    robert.die()
    assert robert.is_alive is False, (
        "Après die(), is_alive devrait être False"
    )


def test_str_repr():
    robert = Baratheon("Robert")
    result_str = str(robert)
    result_repr = repr(robert)
    assert (
        "Baratheon" in result_str
    ), "__str__ doit contenir 'Baratheon'"
    assert (
        "Baratheon" in result_repr
    ), "__repr__ doit contenir 'Baratheon'"


def test_create_lannister():
    jaime = Lannister.create_lannister("Jaime", True)
    assert isinstance(jaime, Lannister), (
        "create_lannister doit renvoyer un Lannister"
    )
    assert jaime.first_name == "Jaime", "first_name incorrect"
    assert jaime.is_alive is True, "is_alive incorrect"


def extra_tests():
    print("\n=== Lancement des tests supplémentaires ex01 ===")
    run_test("Init Baratheon", test_baratheon_init)
    run_test("Init Lannister", test_lannister_init)
    run_test("Méthode die()", test_die_method)
    run_test("__str__ et __repr__ contiennent le nom de famille",
             test_str_repr)
    run_test("Méthode create_lannister()", test_create_lannister)
    print("=== Fin des tests ===")


def subject_tests():
    print("=== Sujet ex01 ===")
    Robert = Baratheon("Robert")
    print(Robert.__dict__)
    print(Robert.__str__)
    print(Robert.__repr__)
    print(Robert.is_alive)
    Robert.die()
    print(Robert.is_alive)
    print(Robert.__doc__)
    print("---")
    Cersei = Lannister("Cersei")
    print(Cersei.__dict__)
    print(Cersei.__str__)
    print(Cersei.is_alive)
    print("---")
    Jaine = Lannister.create_lannister("Jaine", True)
    print(
        f"Name : {Jaine.first_name, type(Jaine).__name__}, "
        f"Alive : {Jaine.is_alive}"
        )
    print("=== Fin des tests sujet ===")


def main():
    subject_tests()
    extra_tests()
    return 0


if __name__ == "__main__":
    main()
