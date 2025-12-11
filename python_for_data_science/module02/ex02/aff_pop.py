from __future__ import annotations
from typing import List, Tuple
import pandas as pd
import matplotlib.pyplot as plt
from difflib import get_close_matches
from load_csv import load
import matplotlib.ticker as mticker


def clean_number_with_suffix(series: pd.Series) -> pd.Series:
    """
    Convertit des nombres éventuellement suffixés par K/M/B
    (kilo/million/billion) en float, en gérant les séparateurs.
    Exemples: '1,234k' -> 1_234_000 ; '2.5M' -> 2_500_000 ;
    '900 B' -> 900_000_000_000
    """
    s = series.astype(str).str.strip()

    suffix = s.str.extract(r'([KkMmBb])\s*$', expand=False)

    base = (
        s.str.replace(r'[KkMmBb]\s*$', '', regex=True)
        .str.replace(",", "", regex=False)
        .str.replace("\u202f", "", regex=False)
        .str.replace("\xa0", "", regex=False)
        .str.replace(" ", "", regex=False)
        )

    nums = pd.to_numeric(base, errors="coerce")

    factor = suffix.map({
        "k": 1e3, "K": 1e3,
        "m": 1e6, "M": 1e6,
        "b": 1e9, "B": 1e9,
    }).fillna(1.0)

    return nums * factor


def extract_year_columns(columns: List[str]) -> Tuple[List[int], List[str]]:
    """
    Return (years_as_int_sorted, year_colnames_sorted) from mixed column names.
    Ignores non-year columns except 'country'.
    """
    pairs: List[Tuple[int, str]] = []
    for c in columns:
        if c == "country":
            continue
        try:
            pairs.append((int(c), c))
        except ValueError:
            continue
    pairs.sort(key=lambda x: x[0])
    years = [y for y, _ in pairs]
    year_cols = [c for _, c in pairs]
    return years, year_cols


def _match_rows_casefold(
    df: pd.DataFrame,
    country: str,
    case_sensitive: bool = False
) -> pd.DataFrame:
    """
    Case-insensitive matching of a country in df['country'].
    Returns a (possibly multi-row) sub-DataFrame.
    """

    if case_sensitive:
        mask = df["country"].astype(str).eq(country)
    else:
        df_processed = df["country"].astype(str).str.strip().str.casefold()
        country_processed = country.strip().casefold()
        mask = df_processed.eq(country_processed)
    return df.loc[mask]


def _suggest_countries(df: pd.DataFrame, query: str, n: int = 3) -> str:
    """
    Suggest close country names for a misspelled query.
    """
    candidates = df["country"].astype(str).unique().tolist()
    sugg = get_close_matches(query, candidates, n=n, cutoff=0.6)
    return ", ".join(sugg)


def compare_countries(
    country_a: str,
    country_b: str,
    csv_path: str = "population_total.csv",
    year_min: int = 1800,
    year_max: int = 2050,
    case_sensitive: bool = False,
) -> None:
    """
    Plot population curves of two countries on [year_min, year_max].

    - Loads `population_total.csv`.
    - Case-insensitive country matching.
    - Handles duplicates by plotting multiple lines per country (#1, #2, ...).
    - Title, axis labels, and legend required by the subject.

    Args:
        country_a (str): First country (e.g., your campus country).
        country_b (str): Second country to compare with.
        csv_path (str): CSV file path.
        year_min (int): Min year to display (inclusive).
        year_max (int): Max year to display (inclusive).
    """
    df = load(csv_path)
    if df is None:
        return

    if "country" not in df.columns:
        print("[Error] 'country' column not found in dataset.")
        return

    # Identify year columns and clamp to [year_min, year_max]
    years_int, year_cols_str = extract_year_columns(df.columns.tolist())
    for c in year_cols_str:
        df[c] = clean_number_with_suffix(df[c])
    if not years_int:
        print("[Error] No year columns detected (e.g., '1800', '1801', ...).")
        return

    # Restrict to requested range and keep only those present in CSV
    years_int = [y for y in years_int if year_min <= y <= year_max]
    if not years_int:
        print(f"[Error] No year in requested range [{year_min}, {year_max}].")
        return
    year_str = [str(y) for y in years_int]  # ensure str colnames

    # Match countries (case-insensitive)
    matches_a = _match_rows_casefold(df, country_a, case_sensitive)
    matches_b = _match_rows_casefold(df, country_b, case_sensitive)

    # Error messages with suggestions if not found
    if matches_a.empty:
        print(f"[Error] Country '{country_a}' not found.")
        s = _suggest_countries(df, country_a.capitalize())
        if s:
            print(f"Did you mean: {s} ?")
        return

    if matches_b.empty:
        print(f"[Error] Country '{country_b}' not found.")
        s = _suggest_countries(df, country_b.capitalize())
        if s:
            print(f"Did you mean: {s} ?")
        return

    plt.figure(figsize=(9, 6))

    # Plot A (one line per duplicate row)
    for idx, row in enumerate(matches_a.itertuples(index=False), start=1):
        row_dict = dict(zip(df.columns, row))
        series = pd.to_numeric(pd.Series(row_dict)[year_str], errors="coerce")
        label = (
            f"{row_dict['country']} #{idx}"
            if len(matches_a) > 1
            else f"{row_dict['country']}"
        )
        plt.plot(
            years_int,
            series.values,
            color="green",
            linewidth=2,
            label=label
            )

    # Plot B (one line per duplicate row)
    for idx, row in enumerate(matches_b.itertuples(index=False), start=1):
        row_dict = dict(zip(df.columns, row))
        series = pd.to_numeric(pd.Series(row_dict)[year_str], errors="coerce")
        label = (
            f"{row_dict['country']} #{idx}"
            if len(matches_b) > 1
            else f"{row_dict['country']}"
        )
        plt.plot(
            years_int,
            series.values,
            color="deepskyblue",
            linewidth=2,
            linestyle="--",
            label=label
        )

    plt.title(
        f"Population Projections: {country_a} vs {country_b}"
        f"(from {year_min} to {year_max})"
        )
    plt.xlabel("Year")
    plt.ylabel("Population")
    plt.legend()

    plt.gca().yaxis.set_major_locator(mticker.MultipleLocator(20_000_000))
    plt.gca().yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"{int(x/1e6)}M")
    )

    plt.tight_layout()
    plt.show()
