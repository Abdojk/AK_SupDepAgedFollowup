"""
grouper.py — Group cases by owner and extract top 3 oldest per owner.
"""

import pandas as pd


def group_by_owner(df: pd.DataFrame) -> dict:
    """
    Returns a dict keyed by owner_email:
    {
        "owner@example.com": {
            "owner_name": "John Smith",
            "owner_email": "owner@example.com",
            "total_cases": 8,
            "top3": [
                {"case_id": "C-1042", "case_title": "...", "age_days": 47, "priority": "High", "created_date": "2024-01-01"},
                ...
            ],
            "all_cases": [...],  # all cases for this owner sorted by age desc
        }
    }
    """
    owners = {}

    for owner_email, group in df.groupby("owner_email"):
        # Sort all cases by age descending (oldest first)
        sorted_group = group.sort_values("age_days", ascending=False)

        all_cases = _to_case_list(sorted_group)
        top3 = all_cases[:3]

        # Use the first record for owner name (normalize casing)
        owner_name = sorted_group.iloc[0]["owner_name"].strip().title()

        owners[owner_email] = {
            "owner_name": owner_name,
            "owner_email": owner_email,
            "total_cases": len(sorted_group),
            "top3": top3,
            "all_cases": all_cases,
        }

    return owners


def _to_case_list(df: pd.DataFrame) -> list[dict]:
    """Convert a DataFrame slice to a clean list of case dicts."""
    cases = []
    for _, row in df.iterrows():
        cases.append({
            "case_id": str(row["case_id"]).strip(),
            "case_title": str(row["case_title"]).strip(),
            "age_days": int(row["age_days"]),
            "priority": str(row["priority"]).strip(),
            "created_date": row["created_date"].strftime("%d %b %Y"),
        })
    return cases
