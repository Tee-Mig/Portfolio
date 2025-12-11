from ft_calculator import calculator

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


def test_add_scalar_updates_state():
    v = calculator([0.0, 1.0, 2.0])
    v + 5
    assert v.result == [5.0, 6.0, 7.0], (
        "Add: état interne incorrect"
    )


def test_mul_scalar_updates_state():
    v = calculator([0.0, 1.0, 2.0, 3.0])
    v * 5
    assert v.result == [0.0, 5.0, 10.0, 15.0], (
        "Mul: état interne incorrect"
    )


def test_sub_scalar_updates_state():
    v = calculator([10.0, 15.0, 20.0])
    v - 5
    assert v.result == [5.0, 10.0, 15.0], (
        "Sub: état interne incorrect"
    )


def test_div_scalar_updates_state():
    v = calculator([10.0, 15.0, 20.0])
    v / 5
    assert v.result == [2.0, 3.0, 4.0], (
        "Div: état interne incorrect"
    )


def test_div_by_zero_no_crash():
    v = calculator([1.0, 2.0, 3.0])
    # Doit juste imprimer le message et ne pas lever d'exception
    v / 0
    assert v.result == [1.0, 2.0, 3.0], (
        "Div/0: l'état ne doit pas changer"
    )


def test_instances_are_independent():
    """Vérifie qu'on n'a pas une liste partagée entre instances."""
    v1 = calculator([0.0, 1.0])
    v2 = calculator([10.0, 20.0])
    v1 + 1
    v2 + 2
    assert v1.result == [1.0, 2.0], (
        "Indépendance: v1 modifié à tort"
    )
    assert v2.result == [12.0, 22.0], (
        "Indépendance: v2 modifié à tort"
    )


def extra_tests():
    """Lance les tests visuels additionnels."""
    print("\n=== Tests supplémentaires ex03 ===")
    run_test(
        "Addition scalaire met à jour l'état",
        test_add_scalar_updates_state
        )
    run_test("Multiplication scalaire met à jour l'état",
             test_mul_scalar_updates_state)
    run_test("Soustraction scalaire met à jour l'état",
             test_sub_scalar_updates_state)
    run_test("Division scalaire met à jour l'état",
             test_div_scalar_updates_state)
    run_test("Division par 0 ne plante pas",
             test_div_by_zero_no_crash)
    run_test("Instances indépendantes",
             test_instances_are_independent)
    print("=== Fin des tests ===")


def subject_tests():
    print("=== Sujet ex03 ===")
    v1 = calculator([0.0, 1.0, 2.0, 3.0, 4.0, 5.0])
    v1 + 5
    print("---")
    v2 = calculator([0.0, 1.0, 2.0, 3.0, 4.0, 5.0])
    v2 * 5
    print("---")
    v3 = calculator([10.0, 15.0, 20.0])
    v3 - 5
    v3 / 5
    # v3 / 0
    print("=== Fin sujet ===")


def main():
    subject_tests()
    extra_tests()
    return 0


if __name__ == "__main__":
    main()
