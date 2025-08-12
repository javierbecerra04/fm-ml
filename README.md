# FM-ML Project

Football Manager meets Machine Learning.

This project aims to explore FM save data (players, matches, teams) to:
- Predict match outcomes
- Cluster players into archetypes
- Estimate transfer value
- Identify opponent weaknesses

## Structure

```
fm-ml/
  data/
    raw/        # CSV exports from FM
    interim/    # cleaned data
    features/   # parquet feature tables
    models/     # saved models
  notebooks/    # Jupyter notebooks for analysis
  src/          # reusable Python modules
```

## Quickstart

1. Export FM data to CSV into `data/raw/`.
2. Create a virtual env and install requirements.
3. Open `notebooks/00_ingest_and_clean.ipynb` to explore, or use the utils:

Python usage:

```python
from src.utils.ingest import load_raw_csvs, save_interim

raw = load_raw_csvs()
# e.g., clean one table then save
# cleaned = some_clean_fn(raw['players'])
# save_interim(cleaned, 'players_cleaned')
```

