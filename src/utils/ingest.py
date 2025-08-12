from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, Tuple

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


def _coerce_numeric_with_percent(col: pd.Series) -> pd.Series:
    """Convert strings with commas and % signs to numeric. If any '%' present, divide by 100."""
    if col.dtype == object:
        s = col.astype(str).str.strip()
        has_percent = s.str.contains("%", regex=False, na=False)
        s = (
            s.replace({"-": None, "": None})
             .str.replace(",", "", regex=False)
             .str.replace("%", "", regex=False)
        )
        num = pd.to_numeric(s, errors="coerce")
        if has_percent.any():
            num = num / 100.0
        return num
    return col


def _split_apps_column(df: pd.DataFrame, col_name: str = "Apps") -> pd.DataFrame:
    """Split an 'Apps' column like '26 (1)' into numeric 'apps' and 'apps_subs'.

    Drops the original textual column to prevent duplicate 'apps' later.
    """
    if col_name in df.columns:
        s = df[col_name].astype(str).str.strip()
        apps = s.str.extract(r"^(\d+)")[0]
        subs = s.str.extract(r"\((\d+)\)")[0]
        df["apps"] = pd.to_numeric(apps, errors="coerce")
        df["apps_subs"] = pd.to_numeric(subs, errors="coerce").fillna(0).astype("Int64")
        df = df.drop(columns=[col_name])
    return df


def _clean_player_name(df: pd.DataFrame, col_name: str = "Player") -> pd.DataFrame:
    if col_name in df.columns:
        df[col_name] = (
            df[col_name]
            .astype(str)
            .str.replace(" - Pick Player", "", regex=False)
            .str.strip()
        )
    return df


def parse_fm_html_table(html_path: Path) -> Tuple[pd.DataFrame, list[str]]:
    """Parse an FM-exported HTML table into a DataFrame.

    Returns df and a list of parsing notes.
    """
    notes: list[str] = []
    try:
        tables = pd.read_html(html_path)
    except Exception as e:
        raise RuntimeError(f"Failed reading HTML tables from {html_path}: {e}") from e

    if not tables:
        raise ValueError(f"No tables found in {html_path}")

    # Heuristic: pick the widest/most columns table
    df = max(tables, key=lambda t: (t.shape[1], t.shape[0]))
    notes.append(f"picked_table_shape={df.shape}")

    # Standardize columns
    df.columns = [str(c).strip().replace("\n", " ") for c in df.columns]

    # Special handling
    df = _split_apps_column(df, "Apps")
    df = _clean_player_name(df, "Player")

    # Coerce numeric where possible (handles %, commas, '-')
    for c in df.columns:
        df[c] = _coerce_numeric_with_percent(df[c])

    return df, notes


def load_raw_htmls(patterns: Iterable[str] = ("*.html", "*.htm")) -> Dict[str, pd.DataFrame]:
    """Load FM HTML exports from data/raw into dict of DataFrames keyed by stem.

    Applies HTML table parsing and basic cleaning.
    """
    out: Dict[str, pd.DataFrame] = {}
    for pat in patterns:
        for fp in RAW_DIR.glob(pat):
            df, notes = parse_fm_html_table(fp)
            _ = notes  # available for logging if needed
            out[fp.stem] = df
    return out


def save_interim(df: pd.DataFrame, name: str) -> Path:
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    fp = INTERIM_DIR / f"{name}.parquet"
    df.to_parquet(fp, index=False)
    return fp
