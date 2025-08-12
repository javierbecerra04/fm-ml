from __future__ import annotations

from typing import Dict
import re
import pandas as pd


def _snake(s: str) -> str:
    s = s.strip().replace("\n", " ")
    s = re.sub(r"[^0-9A-Za-z]+", "_", s)
    s = re.sub(r"_+", "_", s)
    return s.strip("_").lower()


def _rename_with_prefix(df: pd.DataFrame, prefix: str, key_cols=("Player",)) -> pd.DataFrame:
    """Rename non-key columns with a prefix to avoid collisions."""
    cols = {}
    for c in df.columns:
        if c in key_cols:
            continue
        cols[c] = f"{_snake(prefix)}__{_snake(str(c))}"
    return df.rename(columns=cols)


def merge_squad_tables(html_tables: Dict[str, pd.DataFrame], key: str = "Player") -> pd.DataFrame:
    """Merge multiple FM squad HTML tables (already parsed to DataFrames) on the Player column.

    - Picks 'squad_1' as base if present, else the first key.
    - Renames non-key columns from other tables with a prefix derived from their filename stem.
    - Returns a wide per-player DataFrame.
    """
    if not html_tables:
        raise ValueError("No HTML tables provided")

    base_key = "squad_1" if "squad_1" in html_tables else sorted(html_tables.keys())[0]
    base = html_tables[base_key].copy()
    # Drop any leftover textual Apps column to avoid duplicate with numeric 'apps'
    if "Apps" in base.columns:
        base = base.drop(columns=["Apps"]) 

    # Ensure the key exists
    if key not in base.columns:
        raise KeyError(f"Base table '{base_key}' missing join key '{key}'")

    # Normalize base columns to snake case for consistency, keep exact 'Player' name
    rename_map = {c: _snake(str(c)) for c in base.columns if c != key}
    base = base.rename(columns=rename_map)

    # Merge others with prefixed columns
    for k, df in html_tables.items():
        if k == base_key:
            continue
        
        # Handle different column names for player identification
        df2 = df.copy()
        player_col = None
        if key in df2.columns:
            player_col = key
        elif "Name" in df2.columns:
            player_col = "Name"
            # Rename to match base table
            df2 = df2.rename(columns={"Name": key})
        
        if player_col is None:
            # skip tables without any player identification column
            continue
            
        # Drop raw 'Apps' textual if present in any other table as well
        if "Apps" in df2.columns:
            df2 = df2.drop(columns=["Apps"]) 
        df2 = _rename_with_prefix(df2, prefix=k, key_cols=(key,))
        base = base.merge(df2, on=key, how="left", suffixes=(None, None))
        
    # Ensure unique column names post-merge
    seen = {}
    unique_cols = []
    for c in base.columns:
        if c in seen:
            seen[c] += 1
            unique_cols.append(f"{c}__dup{seen[c]}")
        else:
            seen[c] = 0
            unique_cols.append(c)
    base.columns = unique_cols

    return base
