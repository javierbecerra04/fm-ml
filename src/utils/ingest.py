from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable

import pandas as pd

from .paths import RAW_DIR, INTERIM_DIR


def load_raw_csvs(patterns: Iterable[str] = ("*.csv",)) -> Dict[str, pd.DataFrame]:
    """Load raw CSVs from data/raw into a dict of DataFrames keyed by stem.

    - patterns: glob patterns to include.
    """
    out: Dict[str, pd.DataFrame] = {}
    for pat in patterns:
        for fp in RAW_DIR.glob(pat):
            try:
                df = pd.read_csv(fp)
            except Exception as e:
                raise RuntimeError(f"Failed reading {fp}: {e}") from e
            key = fp.stem
            out[key] = df
    return out


def save_interim(df: pd.DataFrame, name: str) -> Path:
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    fp = INTERIM_DIR / f"{name}.parquet"
    df.to_parquet(fp, index=False)
    return fp
