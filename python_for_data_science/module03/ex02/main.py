from DiamondTrap import King
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


def test_king_defaults():
    """Vérifie les valeurs par défaut à l’instanciation."""
    j = King("Joffrey")
    assert j.first_name == "Joffrey", "first_name incorrect"
    assert j.is_alive is True, "is_alive par défaut devrait être True"
    assert j.family_name == "Baratheon", "family_name doit être Baratheon"
    assert j.eyes == "brown", "eyes par défaut devrait être 'brown'"
    assert j.hairs == "dark", "hairs par défaut devrait être 'dark'"


def test_setters_getters():
    """Vérifie set_eyes / set_hairs et get_eyes / get_hairs."""
    j = King("Joffrey")
    j.set_eyes("blue")
    j.set_hairs("light")
    assert j.get_eyes() == "blue", "get_eyes doit renvoyer 'blue'"
    assert j.get_hairs() == "light", "get_hairs doit renvoyer 'light'"
    assert j.eyes == "blue", "attribut eyes non modifié"
    assert j.hairs == "light", "attribut hairs non modifié"


def test_diamond_inheritance_instanceof():
    """King est bien instance des deux familles (héritage diamant)."""
    j = King("Joffrey")
    assert isinstance(j, Baratheon), "King doit être Baratheon"
    assert isinstance(j, Lannister), "King doit être Lannister"


def test_c3_linearization_order():
    """Vérifie l’ordre MRO: King(Baratheon, Lannister) -> C3."""
    mro = King.mro()
    # mro: [King, Baratheon, Lannister, Character, ABC, object]
    assert mro[1] is Baratheon, "MRO: Baratheon attendu en 1"
    assert mro[2] is Lannister, "MRO: Lannister attendu en 2"


def extra_tests():
    """Lance les tests visuels additionnels."""
    print("\n=== Tests supplémentaires ex02 ===")
    run_test("Init King: valeurs par défaut", test_king_defaults)
    run_test("Setters/Getters (eyes/hairs)", test_setters_getters)
    run_test(
        "InstanceOf Baratheon/Lannister",
        test_diamond_inheritance_instanceof,
    )
    run_test("Ordre C3 (MRO) attendu", test_c3_linearization_order)
    print("=== Fin des tests ===")


def subject_tests():
    print("=== Sujet ex02 ===")
    Joffrey = King("Joffrey")
    print(Joffrey.__dict__)
    Joffrey.set_eyes("blue")
    Joffrey.set_hairs("light")
    print(Joffrey.get_eyes())
    print(Joffrey.get_hairs())
    print(Joffrey.__dict__)
    print("=== Fin des tests sujet ===")


def main():
    subject_tests()
    extra_tests()
    return 0


if __name__ == "__main__":
    main()
