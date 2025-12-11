from projection_life import plot_projection
import os
import csv
import stat

GDP_FILE = "income_per_person_gdppercapita_ppp_inflation_adjusted_test.csv"
LIFE_FILE = "life_expectancy_years_test.csv"


def ft_write_csv(
    path: str,
    header: list[str],
    rows: list[list[object]]
) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def ft_rm(path: str) -> None:
    if os.path.exists(path):
        try:
            os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)  # rw pour l'owner
        except Exception:
            pass
        try:
            os.remove(path)
        except Exception:
            pass


def run_plot_projection_error_tests(year: int = 1900) -> None:
    """
    Teste les cas d'erreurs de plot_projection (ex03) en écrivant/épurant
    les fichiers par défaut utilisés par le module.

      1) Fichier GDP manquant
      2) Fichier LIFE manquant
      3) Fichier GDP vide
      4) Fichier LIFE vide
      5) Fichier GDP illisible (chmod 000)
      6) Colonne 'country' absente dans GDP
      7) Colonne 'country' absente dans LIFE
      8) Année manquante dans GDP
      9) Année manquante dans LIFE
     10) Aucune colonne d'années dans GDP
     11) Aucune colonne d'années dans LIFE
     12) Données non numériques -> tout NaN après nettoyage
     13) Cas OK minimal pour vérifier que ça trace sans erreur
    """
    print("\n=== 1) Missing GDP file ===")
    ft_rm(GDP_FILE)
    ft_rm(LIFE_FILE)
    ft_write_csv(
        LIFE_FILE,
        ["country", str(year)],
        [["Afghanistan", 40.0], ["Angola", 27.0]]
        )
    plot_projection(year, GDP_FILE, LIFE_FILE)
    ft_rm(LIFE_FILE)

    print("\n=== 2) Missing LIFE file ===")
    ft_rm(GDP_FILE)
    ft_rm(LIFE_FILE)
    ft_write_csv(
        GDP_FILE,
        ["country", str(year)],
        [["Afghanistan", 1000], ["Angola", 1800]]
        )
    plot_projection(year, GDP_FILE, LIFE_FILE)
    ft_rm(GDP_FILE)

    print("\n=== 3) Empty GDP file ===")
    ft_rm(GDP_FILE)
    ft_rm(LIFE_FILE)
    with open(GDP_FILE, "w", encoding="utf-8"):
        pass
    ft_write_csv(
        LIFE_FILE,
        ["country", str(year)],
        [["Afghanistan", 40.0], ["Angola", 27.0]]
        )
    plot_projection(year, GDP_FILE, LIFE_FILE)
    ft_rm(GDP_FILE)
    ft_rm(LIFE_FILE)

    print("\n=== 4) Empty LIFE file ===")
    ft_rm(GDP_FILE)
    ft_rm(LIFE_FILE)
    ft_write_csv(
        GDP_FILE,
        ["country", str(year)],
        [["Afghanistan", 1000], ["Angola", 1800]]
        )
    with open(LIFE_FILE, "w", encoding="utf-8"):
        pass
    plot_projection(year, GDP_FILE, LIFE_FILE)
    ft_rm(GDP_FILE)
    ft_rm(LIFE_FILE)

    print("\n=== 5) GDP no read permission (chmod 000) ===")
    ft_rm(GDP_FILE)
    ft_rm(LIFE_FILE)
    ft_write_csv(
        GDP_FILE,
        ["country", str(year)],
        [["Afghanistan", 1000], ["Angola", 1800]]
        )
    ft_write_csv(
        LIFE_FILE,
        ["country", str(year)],
        [["Afghanistan", 40.0], ["Angola", 27.0]]
        )
    os.chmod(GDP_FILE, 0)
    try:
        plot_projection(year, GDP_FILE, LIFE_FILE)
    finally:
        ft_rm(GDP_FILE)
        ft_rm(LIFE_FILE)

    print("\n=== 6) Missing 'country' in GDP ===")
    ft_rm(GDP_FILE)
    ft_rm(LIFE_FILE)
    ft_write_csv(
        GDP_FILE,
        ["nation", str(year)],
        [["Afghanistan", 1000], ["Angola", 1800]]
        )
    ft_write_csv(
        LIFE_FILE,
        ["country", str(year)],
        [["Afghanistan", 40.0], ["Angola", 27.0]]
        )
    plot_projection(year, GDP_FILE, LIFE_FILE)
    ft_rm(GDP_FILE)
    ft_rm(LIFE_FILE)

    print("\n=== 7) Missing 'country' in LIFE ===")
    ft_rm(GDP_FILE)
    ft_rm(LIFE_FILE)
    ft_write_csv(
        GDP_FILE,
        ["country", str(year)],
        [["Afghanistan", 1000], ["Angola", 1800]]
        )
    ft_write_csv(
        LIFE_FILE,
        ["nation", str(year)],
        [["Afghanistan", 40.0], ["Angola", 27.0]]
        )
    plot_projection(year, GDP_FILE, LIFE_FILE)
    ft_rm(GDP_FILE)
    ft_rm(LIFE_FILE)

    print("\n=== 8) Year missing in GDP ===")
    ft_rm(GDP_FILE)
    ft_rm(LIFE_FILE)
    ft_write_csv(
        GDP_FILE,
        ["country", str(year + 1)],
        [["Afghanistan", 1100], ["Angola", 1900]]
        )
    ft_write_csv(
        LIFE_FILE,
        ["country", str(year)],
        [["Afghanistan", 40.0], ["Angola", 27.0]]
        )
    plot_projection(year, GDP_FILE, LIFE_FILE)
    ft_rm(GDP_FILE)
    ft_rm(LIFE_FILE)

    print("\n=== 9) Year missing in LIFE ===")
    ft_rm(GDP_FILE)
    ft_rm(LIFE_FILE)
    ft_write_csv(
        GDP_FILE,
        ["country", str(year)],
        [["Afghanistan", 1000], ["Angola", 1800]]
        )
    ft_write_csv(
        LIFE_FILE,
        ["country", str(year + 1)],
        [["Afghanistan", 41.0], ["Angola", 27.5]]
        )
    plot_projection(year, GDP_FILE, LIFE_FILE)
    ft_rm(GDP_FILE)
    ft_rm(LIFE_FILE)

    print("\n=== 10) No year columns in GDP ===")
    ft_rm(GDP_FILE)
    ft_rm(LIFE_FILE)
    ft_write_csv(
        GDP_FILE,
        ["country"],
        [["Afghanistan"], ["Angola"]]
        )
    ft_write_csv(
        LIFE_FILE,
        ["country", str(year)],
        [["Afghanistan", 40.0], ["Angola", 27.0]]
        )
    plot_projection(year, GDP_FILE, LIFE_FILE)
    ft_rm(GDP_FILE)
    ft_rm(LIFE_FILE)

    print("\n=== 11) No year columns in LIFE ===")
    ft_rm(GDP_FILE)
    ft_rm(LIFE_FILE)
    ft_write_csv(
        GDP_FILE,
        ["country", str(year)],
        [["Afghanistan", 1000], ["Angola", 1800]]
        )
    ft_write_csv(
        LIFE_FILE,
        ["country"],
        [["Afghanistan"], ["Angola"]]
        )
    plot_projection(year, GDP_FILE, LIFE_FILE)
    ft_rm(GDP_FILE)
    ft_rm(LIFE_FILE)

    print("\n=== 12) Non-numeric values → all NaN after cleaning ===")
    ft_rm(GDP_FILE)
    ft_rm(LIFE_FILE)
    # Valeurs non numériques qui deviendront NaN après clean_to_numeric
    ft_write_csv(
        GDP_FILE,
        ["country", str(year)],
        [["Afghanistan", "foo"], ["Angola", "bar"]]
        )
    ft_write_csv(
        LIFE_FILE,
        ["country", str(year)],
        [["Afghanistan", "baz"], ["Angola", "qux"]]
        )
    plot_projection(year, GDP_FILE, LIFE_FILE)
    ft_rm(GDP_FILE)
    ft_rm(LIFE_FILE)

    print("\n=== 13) OK minimal (devrait tracer sans erreur) ===")
    ft_rm(GDP_FILE)
    ft_rm(LIFE_FILE)
    # Données minimalistes (cohérentes avec ta structure)
    ft_write_csv(
        GDP_FILE,
        ["country", str(year)],
        [["Afghanistan", 1000], ["Angola", 1800]]
        )
    ft_write_csv(
        LIFE_FILE,
        ["country", str(year)],
        [["Afghanistan", 40.0], ["Angola", 27.0]]
        )
    plot_projection(year, GDP_FILE, LIFE_FILE)
    ft_rm(GDP_FILE)
    ft_rm(LIFE_FILE)

    print("\n=== DONE ===")


def main() -> None:
    year = 1900
    plot_projection(year)

    run_plot_projection_error_tests(year)


if __name__ == "__main__":
    main()
