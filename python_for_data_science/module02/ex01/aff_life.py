from typing import List, Tuple
import pandas as pd
import matplotlib.pyplot as plt
from difflib import get_close_matches
from load_csv import load


def extract_year_columns(columns: List[str]) -> Tuple[List[int], List[str]]:
    """
    From a list of column names, keep only those that
    are years (int-convertible), returned as sorted lists
    of (years, original column names).

    Args:
        columns (List[str]): DataFrame column names.

    Returns:
        Tuple[List[int], List[str]]: (years as ints sorted ASC,
        corresponding column names)
    """
    pairs: List[Tuple[int, str]] = []
    for col in columns:
        if col == "country":
            continue
        try:
            pairs.append((int(col), col))
        except ValueError:
            continue
    pairs.sort(key=lambda x: x[0])
    years = [y for y, _ in pairs]
    year_cols = [c for _, c in pairs]
    return years, year_cols


def draw_country(
    country: str,
    file_to_load: str = "life_expectancy_years.csv",
    case_sensitive: bool = False
) -> None:
    """
    Display the life expectancy evolution for a given country.
    If multiple rows match the country (duplicates), plot all of them.

    Args:
        country (str): Country name to display.
        case_insensitive (bool): If True, match is case-insensitive and
        trims spaces.
    """
    dataset = load(file_to_load)
    if dataset is None:
        print("[Error] Dataset could not be loaded.")
        return

    if "country" not in dataset.columns:
        print("[Error] 'country' column is missing from dataset.")
        return

    if case_sensitive:
        mask = dataset["country"].astype(str).eq(country)
    else:
        dataset_processed = (
            dataset["country"]
            .astype(str)
            .str.strip()
            .str
            .casefold()
        )
        country_processed = country.strip().casefold()
        mask = dataset_processed.eq(country_processed)

    matches = dataset.loc[mask]
    if matches.empty:
        print(f"[Error] Country '{country}' not found in dataset.")
        candidates = dataset["country"].astype(str).unique().tolist()
        suggestions = get_close_matches(country, candidates, n=2, cutoff=0.7)
        if suggestions:
            print(f"Did you mean: {', '.join(suggestions)} ?")
        return

    int_years, year_str = extract_year_columns(dataset.columns.tolist())
    if not int_years:
        print("[Error] No year columns found in dataset.")
        return

    if len(matches) > 1:
        print(f"[Warning] Multiple entries found for '{country}' "
              f"({len(matches)} rows). Plotting all of them.")

    plt.figure(figsize=(6, 5))

    for idx, row in enumerate(matches.itertuples(index=False), start=1):
        row_dict = dict(zip(dataset.columns, row))
        values = pd.to_numeric(pd.Series(row_dict)[year_str], errors="coerce")
        label = (f"{row_dict['country']} #{idx}"
                 if len(matches) > 1 else f"{row_dict['country']}")
        plt.plot(int_years, values, linewidth=2, label=label)

    plt.title(f"{country.capitalize()} Life expectancy Projections")
    plt.xlabel("Year")
    plt.ylabel("Life Expectancy")
    plt.legend()
    plt.tight_layout()
    plt.show()
