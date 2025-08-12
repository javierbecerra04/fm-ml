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
2. Install requirements: `pip install -r requirements.txt`
3. Start with `notebooks/00_ingest_and_clean.ipynb`.

