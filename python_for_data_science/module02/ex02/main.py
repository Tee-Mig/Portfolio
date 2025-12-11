from aff_pop import compare_countries
import os
import csv
import stat


def _write_csv(path: str, header: list[str], rows: list[list[object]]) -> None:
    """Écrit un petit CSV (UTF-8, newline correct)."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def run_compare_countries_error_tests() -> None:
    """
    Teste les principaux cas d'erreurs de compare_countries:

      1) Fichier introuvable
      2) Fichier vide
      3) Fichier illisible (permissions)
      4) Colonne 'country' absente
      5) Pays A non trouvé
      6) Pays B non trouvé
      7) Aucune colonne d'années
      8) Aucune année dans la plage demandée
      9) Fichier 'corrompu' (Valid format)
    """
    print("\n=== 1) Missing file ===")
    compare_countries("France", "Germany", csv_path="__does_not_exist__.csv")

    print("\n=== 2) Empty file ===")
    empty_path = "tmp_empty.csv"
    with open(empty_path, "w", encoding="utf-8"):
        pass
    compare_countries("France", "Germany", csv_path=empty_path)
    os.remove(empty_path)

    print("\n=== 3) No read permission (chmod 000) ===")
    no_perm_path = "tmp_no_perm.csv"
    _write_csv(
        no_perm_path,
        ["country", "1800", "1801"],
        [["France", 30, 31], ["Germany", 28, 29]],
    )
    os.chmod(no_perm_path, 0)
    try:
        compare_countries("France", "Germany", csv_path=no_perm_path)
    finally:
        os.chmod(no_perm_path, stat.S_IWUSR | stat.S_IRUSR)
        os.remove(no_perm_path)

    print("\n=== 4) Missing 'country' column ===")
    no_country_col = "tmp_no_country_col.csv"
    _write_csv(
        no_country_col,
        ["nation", "1800", "1801"],
        [["France", 30, 31], ["Germany", 28, 29]],
    )
    compare_countries("France", "Germany", csv_path=no_country_col)
    os.remove(no_country_col)

    print("\n=== 5) Country A not found ===")
    a_not_found = "tmp_a_not_found.csv"
    _write_csv(
        a_not_found,
        ["country", "1800", "1801"],
        [["Spain", 28, 29], ["Germany", 30, 31]],
    )
    compare_countries("France", "Germany", csv_path=a_not_found)
    os.remove(a_not_found)

    print("\n=== 6) Country B not found ===")
    b_not_found = "tmp_b_not_found.csv"
    _write_csv(
        b_not_found,
        ["country", "1800", "1801"],
        [["France", 30, 31], ["Spain", 28, 29]],
    )
    compare_countries("France", "Germany", csv_path=b_not_found)
    os.remove(b_not_found)

    print("\n=== 7) No year columns ===")
    no_years = "tmp_no_years.csv"
    _write_csv(no_years, ["country"], [["France"], ["Germany"]])
    compare_countries("France", "Germany", csv_path=no_years)
    os.remove(no_years)

    print("\n=== 8) No year in requested range ===")
    ok_small = "tmp_ok_small.csv"
    _write_csv(
        ok_small,
        ["country", "1800", "1801", "1802"],
        [["France", 30, 31, 32], ["Germany", 28, 29, 30]],
    )
    # Demander une plage hors des colonnes présentes -> erreur attendue
    compare_countries("France", "Germany", csv_path=ok_small,
                      year_min=3000, year_max=3010)
    os.remove(ok_small)

    print("\n=== 9) Corrupted line length (Valid) ===")
    corrupt = "tmp_corrupt.csv"
    # 3 colonnes d'en-tête, mais 2 valeurs sur la 2e ligne
    with open(corrupt, "w", encoding="utf-8") as f:
        f.write("country,1800,1801\nFrance,30,31\nGermany,28\n")
    compare_countries("France", "Germany", csv_path=corrupt)
    os.remove(corrupt)

    print("\n=== DONE ===")


def main() -> None:
    my_campus = "France"
    country_to_compare = input(
        f"Votre campus est actuellement en {my_campus}."
        " \nEntrez le pays que vous voulez comparer : "
    )
    compare_countries(my_campus, country_to_compare)

    run_compare_countries_error_tests()


if __name__ == "__main__":
    main()
