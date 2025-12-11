import pandas as pd
from typing import Optional


def load(path: str) -> Optional[pd.DataFrame]:
    """
    Load a dataset from a CSV file.

    Args:
        path (str): Path to the CSV file.

    Returns:
        pd.DataFrame | None: The loaded dataset if successful, else None.
    """
    try:
        dataset = pd.read_csv(path)
        print(f"Loading dataset of dimensions {dataset.shape}")
        return dataset
    except Exception as error:
        print(f"[Error] Cannot load dataset: {error}")
        return None
