
from ft_calculator import calculator
from io import StringIO
from contextlib import redirect_stdout

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


def capture_output(callable_):
    """Capture stdout pendant l'appel à callable_ et renvoie la chaîne."""
    buf = StringIO()
    with redirect_stdout(buf):
        callable_()
    return buf.getvalue()


def test_dotproduct_prints_expected():
    a = [5, 10, 2]
    b = [2, 4, 3]
    out = capture_output(lambda: calculator.dotproduct(a, b))
    expected = "Dot product is: 56\n"
    assert out == expected, f"sortie={out!r}, attendu={expected!r}"


def test_add_vec_prints_expected():
    a = [5, 10, 2]
    b = [2, 4, 3]
    out = capture_output(lambda: calculator.add_vec(a, b))
    expected = "Add Vector is: [7.0, 14.0, 5.0]\n"
    assert out == expected, f"sortie={out!r}, attendu={expected!r}"


def test_sous_vec_prints_expected():
    a = [5, 10, 2]
    b = [2, 4, 3]
    out = capture_output(lambda: calculator.sous_vec(a, b))
    expected = "Sous Vector is: [3.0, 6.0, -1.0]\n"
    assert out == expected, f"sortie={out!r}, attendu={expected!r}"


def test_static_methods_callable_without_instance():
    """Vérifie qu'on peut appeler sans instancier la classe."""
    a = [1.0, 2.0]
    b = [3.0, 4.0]
    # Ces appels ne doivent pas lever d'exception
    capture_output(lambda: calculator.dotproduct(a, b))
    capture_output(lambda: calculator.add_vec(a, b))
    capture_output(lambda: calculator.sous_vec(a, b))


def extra_tests():
    """Lance les tests visuels additionnels."""
    print("\n=== Tests supplémentaires ex04 ===")
    run_test("Dot product: sortie conforme", test_dotproduct_prints_expected)
    run_test("Add vector: sortie conforme", test_add_vec_prints_expected)
    run_test("Sous vector: sortie conforme", test_sous_vec_prints_expected)
    run_test(
        "Appel statique sans instance",
        test_static_methods_callable_without_instance,
    )
    print("=== Fin des tests ===")


def subject_tests():
    print("=== Sujet ex04 ===")
    a = [5, 10, 2]
    b = [2, 4, 3]
    calculator.dotproduct(a, b)
    calculator.add_vec(a, b)
    calculator.sous_vec(a, b)
    print("=== Fin sujet ===")


def main():
    subject_tests()
    extra_tests()
    return 0


if __name__ == "__main__":
    main()
