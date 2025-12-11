from load_csv import load


def test_errors() -> None:
    """
    Run a few error tests on the load function.
    """
    print("=== Testing errors ===")

    # Cas 1 : chemin inexistant
    print("\nCase 1: Wrong path")
    print(load("wrong_file.csv"))

    # Cas 2 : fichier vide
    print("\nCase 2: Empty file")
    print(load("empty.csv"))

    # Cas 3 : mauvais format (ex. fichier texte)
    print("\nCase 3: Wrong format")
    print(load("not_a_csv.txt"))

    # Cas 4 : mauvais type (ex. None)
    print("\nCase 4: Wrong type")
    print(load(None))

    # Cas 5 : mauvais type 2 (ex. True)
    print("\nCase 5: Wrong type 2")
    print(load(True))

    # Cas 5 : corrupted file (ex. no right)
    print("\nCase 5: No right file")
    print(load("no_right.csv"))


def main():
    dataset = load("life_expectancy_years.csv")
    if dataset is not None:
        print(dataset.head())

    test_errors()


if __name__ == "__main__":
    main()
