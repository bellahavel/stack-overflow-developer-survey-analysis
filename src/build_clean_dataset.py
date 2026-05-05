from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    # Make sure the script can import the shared cleaning code from src/.
    sys.path.insert(0, str(ROOT))

from src.dashboard_data import KEEP_COLS, prepare_dashboard_dataframe

RAW_PATH = ROOT / "data" / "survey_results_public.csv"
CLEAN_PATH = ROOT / "data" / "cleaned_stackoverflow_data.csv"


def main():
    # Read the raw survey file and apply the same cleaning logic used by the dashboard.
    df = pd.read_csv(RAW_PATH, low_memory=False)
    cleaned = prepare_dashboard_dataframe(df)

    # Keep the saved file small by exporting only the columns the app needs.
    export_cols = [col for col in KEEP_COLS if col in cleaned.columns]
    cleaned[export_cols].to_csv(CLEAN_PATH, index=False)
    size_mb = CLEAN_PATH.stat().st_size / (1024 * 1024)
    print(f"Wrote {CLEAN_PATH} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()
