from aff_life import draw_country
import os
import csv
from load_csv import load


def write_csv(path: str, header: list[str], rows: list[list]) -> None:
    """Helper: create a small CSV file."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def run_draw_country_error_tests(country: str) -> None:
    """
    Run several error scenarios for draw_country:
      1) Missing file
      2) Empty file
      3) 'Corrupted' file (valid format)
      4) No 'country' column
      5) Country not found
      6) No year columns
    """

    print("\n=== 1) Missing file ===")
    draw_country("France", file_to_load="file_does_not_exist.csv")

    print("\n=== Test 2: Empty file ===")
    empty_path = "empty.csv"
    with open(empty_path, "w", encoding="utf-8"):
        pass
    load(empty_path)
    os.remove(empty_path)

    print("\n=== Test 3: Corrupted file(Valid) ===")
    corrupt_path = "corrupt.csv"
    with open(corrupt_path, "w", encoding="utf-8") as f:
        f.write("country,1800,1801\nFrance,30,31\nSpain,28")
    load(corrupt_path)
    draw_country(country, corrupt_path, False)
    os.remove(corrupt_path)

    print("\n=== 4) No 'country' column ===")
    no_country_path = "no_country.csv"
    write_csv(
        no_country_path,
        ["nation", "1800", "1801"],
        [["France", 30, 31], ["Spain", 28, 29]]
    )
    draw_country("France", file_to_load=no_country_path)
    os.remove(no_country_path)

    print("\n=== 5) Country not found ===")
    country_not_found_path = "not_found.csv"
    write_csv(
        country_not_found_path,
        ["country", "1800", "1801"],
        [["Spain", 28, 29], ["Italy", 30, 31]]
    )
    draw_country("France", file_to_load=country_not_found_path)
    os.remove(country_not_found_path)

    print("\n=== 6) No year columns ===")
    no_years_path = "no_years.csv"
    write_csv(no_years_path, ["country"], [["France"], ["Spain"]])
    draw_country("France", file_to_load=no_years_path)
    os.remove(no_years_path)


def main() -> None:
    country = input("Entrez le pays que vous voulez afficher : ")
    draw_country(country)

    run_draw_country_error_tests(country)


if __name__ == "__main__":
    main()
