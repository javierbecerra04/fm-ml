from pathlib import Path

# Project root is two levels up from this file: src/utils/paths.py -> project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
FEATURES_DIR = DATA_DIR / "features"
MODELS_DIR = DATA_DIR / "models"

for p in [DATA_DIR, RAW_DIR, INTERIM_DIR, FEATURES_DIR, MODELS_DIR]:
    p.mkdir(parents=True, exist_ok=True)
