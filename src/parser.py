"""
parser.py — Load and validate the CRM cases input file.
"""

import sys
import pandas as pd
from datetime import date

# Map normalised CRM-export column names → internal names
COLUMN_MAP = {
    "(do_not_modify)_case": "case_id",
    "owner": "owner_name",
    "created_on": "created_date",
}

# Owner name → email lookup (info-sys.com domain)
OWNER_EMAIL_MAP = {
    "Fadi Hanna": "FHanna@info-sys.com",
    "Georges Mouaikel": "GMouaikel@info-sys.com",
    "Jana Sweid": "JSweid@info-sys.com",
    "Mennatullah El Bahr": "MElBahr@info-sys.com",
    "Rebecca Estephan": "REstephan@info-sys.com",
}

# Manager's own cases are excluded from follow-up emails
MANAGER_OWNER_NAME = "Abdo Khoury"

REQUIRED_COLUMNS = {"case_id", "case_title", "owner_name", "owner_email", "created_date"}
OPTIONAL_COLUMNS = {"priority"}
VALID_PRIORITIES = {"High", "Normal", "Medium", "Low"}


def load_and_validate(filepath: str) -> pd.DataFrame:
    """Load cases CSV, validate schema, calculate age in days."""

    # Load file
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"\n[ERROR] File not found: {filepath}")
        print("  Place your cases export at data/cases.csv and retry.\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Could not read file: {e}\n")
        sys.exit(1)

    # Normalize column names (lowercase, spaces → underscores)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Rename CRM-export columns to internal names
    df = df.rename(columns=COLUMN_MAP)

    # Derive owner_email from owner_name using the lookup map
    df["owner_name"] = df["owner_name"].str.strip()
    df["owner_email"] = df["owner_name"].map(OWNER_EMAIL_MAP)

    # Filter out manager's own cases
    manager_count = (df["owner_name"] == MANAGER_OWNER_NAME).sum()
    if manager_count > 0:
        print(f"  Excluding {manager_count} case(s) owned by {MANAGER_OWNER_NAME} (manager).")
        df = df[df["owner_name"] != MANAGER_OWNER_NAME]

    # Filter out Raji Aoun's cases
    raji_count = (df["owner_name"] == "Raji Aoun").sum()
    if raji_count > 0:
        print(f"  Excluding {raji_count} case(s) owned by Raji Aoun.")
        df = df[df["owner_name"] != "Raji Aoun"]

    # Warn about unmapped owners
    unmapped = df[df["owner_email"].isna()]["owner_name"].unique()
    if len(unmapped) > 0:
        print(f"  [WARN] No email mapping for owner(s): {list(unmapped)} — these rows will be dropped.")

    # Validate required columns
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        print(f"\n[ERROR] Input file is missing required column(s): {missing}")
        print(f"  Found columns: {list(df.columns)}\n")
        sys.exit(1)

    # Fill optional priority column if missing
    if "priority" not in df.columns:
        df["priority"] = "Medium"
    else:
        df["priority"] = df["priority"].fillna("Medium")
        # Normalize casing
        df["priority"] = df["priority"].str.strip().str.capitalize()
        invalid_priority = df[~df["priority"].isin(VALID_PRIORITIES)]
        if not invalid_priority.empty:
            print(f"  [WARN] {len(invalid_priority)} row(s) have invalid priority values — defaulting to 'Medium'.")
            df.loc[~df["priority"].isin(VALID_PRIORITIES), "priority"] = "Medium"

    # Parse dates and calculate age
    try:
        df["created_date"] = pd.to_datetime(df["created_date"])
    except Exception as e:
        print(f"\n[ERROR] Could not parse 'created_date' column: {e}")
        print("  Ensure dates are in a parseable date format.\n")
        sys.exit(1)

    today = pd.Timestamp(date.today())
    df["age_days"] = (today - df["created_date"]).dt.days

    # Drop rows with missing critical fields
    before = len(df)
    df = df.dropna(subset=["owner_email", "case_id"])
    dropped = before - len(df)
    if dropped > 0:
        print(f"  [WARN] Dropped {dropped} row(s) with missing owner_email or case_id.")

    print(f"  Loaded {len(df)} valid case(s) from {filepath}")
    return df
