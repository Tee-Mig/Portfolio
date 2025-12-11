from __future__ import annotations

from typing import List, Tuple, Optional
import pandas as pd
import matplotlib.pyplot as plt
from load_csv import load
import matplotlib.ticker as mticker


def extract_year_columns(columns: List[str]) -> Tuple[List[int], List[str]]:
    """
    Identify columns whose names are convertible to int (years).
    Returns (years_as_int_sorted, corresponding_name_list_sorted).
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
    return [y for y, _ in pairs], [c for _, c in pairs]


def clean_to_numeric(series_like: pd.Series) -> pd.Series:
    """
    Convert a Series to numeric reliably:
    - cast to string
    - remove common thousand separators and non-breaking spaces
    - coerce errors to NaN
    """
    s = pd.Series(series_like).astype(str)
    s = (
        s.str.replace(",", "", regex=False)
         .str.replace("\u202f", "", regex=False)
         .str.replace("\xa0", "", regex=False)
         .str.replace(" ", "", regex=False)
    )
    return pd.to_numeric(s, errors="coerce")


def prepare_projection_dataframe(
    year: int,
    gdp_csv: str,
    life_csv: str,
) -> Optional[pd.DataFrame]:
    """
    Load, align and prepare the 1900 (or any year) projection dataframe.

    Returns:
        DataFrame with columns: ['country', 'gdp', 'life'] filtered for
        the given year,
        or None on error.
    """
    gdp_df = load(gdp_csv)
    if gdp_df is None:
        return None
    life_df = load(life_csv)
    if life_df is None:
        return None

    if "country" not in gdp_df.columns or "country" not in life_df.columns:
        print("[Error] 'country' column missing in one of the datasets.")
        return None

    g_years, g_cols = extract_year_columns(gdp_df.columns.tolist())
    l_years, l_cols = extract_year_columns(life_df.columns.tolist())
    if not g_years or not l_years:
        print("[Error] No year columns detected in one of the datasets.")
        return None

    if str(year) not in gdp_df.columns or str(year) not in life_df.columns:
        print(f"[Error] Year {year} not found in one of the datasets.")
        return None

    g_keep = ["country", str(year)]
    l_keep = ["country", str(year)]
    gdp_year = gdp_df[g_keep].rename(columns={str(year): "gdp"})
    life_year = life_df[l_keep].rename(columns={str(year): "life"})

    gdp_year["gdp"] = clean_to_numeric(gdp_year["gdp"])
    life_year["life"] = clean_to_numeric(life_year["life"])

    merged = pd.merge(gdp_year, life_year, on="country", how="inner")

    merged = merged.dropna(subset=["gdp", "life"])

    if merged.empty:
        print(
            "[Error] No data to plot after"
            " cleaning (all NaN or no overlap).")
        return None

    return merged


def plot_projection(
    year: int = 1900,
    gdp_csv: str = "income_per_person_gdppercapita_ppp_inflation_adjusted.csv",
    life_csv: str = "life_expectancy_years.csv"
) -> None:
    """
    Plot the projection of life expectancy vs GDP per capita (PPP)
    for the given year (default 1900), each point = a country.

    Graph includes:
      - Title
      - Axis labels
      - Legend (marker meaning)
      - Year displayed in the title
      - Log scale on X (GDP) for readability
    """
    df = prepare_projection_dataframe(year, gdp_csv, life_csv)
    if df is None:
        return

    plt.figure(figsize=(6, 5))
    plt.scatter(df["gdp"], df["life"])

    plt.xscale("log")
    plt.title(f"{year}")
    plt.xlabel("Gross domestic product")
    plt.ylabel("Life expectancy")

    ax = plt.gca()
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(
        lambda x, pos: f"{int(x/1000)}k" if x >= 1000 else str(int(x))
    ))

    plt.tight_layout()
    plt.show()
