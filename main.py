"""
CRM Case Follow-Up Email Automation
Entry point — run with --send to actually deliver emails, default is dry-run.
"""

import argparse
import sys
from src.parser import load_and_validate
from src.grouper import group_by_owner
from src.email_builder import build_drafts
from src.email_sender import send_emails
from src.logger import init_log, print_summary


def main():
    parser = argparse.ArgumentParser(description="CRM Case Follow-Up Email Automation")
    parser.add_argument("--input", default="data/cases.csv", help="Path to cases CSV file")
    parser.add_argument("--send", action="store_true", help="Actually send emails (default: dry-run)")
    parser.add_argument("--owner", default=None, help="Send only to a specific owner email")
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("  CRM Case Follow-Up Email Automation")
    print(f"  Mode: {'LIVE SEND' if args.send else 'DRY RUN (drafts only)'}")
    print("=" * 60 + "\n")

    # Step 1: Load and validate input
    print("[1/4] Loading and validating cases...")
    cases_df = load_and_validate(args.input)

    # Step 2: Group by owner, top 3 oldest per owner
    print("[2/4] Grouping by owner and calculating case ages...")
    owners = group_by_owner(cases_df)

    # Print preview summary
    print("\n--- Owner Summary ---")
    for owner_email, data in owners.items():
        if args.owner and owner_email != args.owner:
            continue
        print(f"\n  {data['owner_name']} ({owner_email})")
        print(f"  Total open cases: {data['total_cases']}")
        print(f"  Top 3 oldest:")
        for i, case in enumerate(data["top3"], 1):
            print(f"    {i}. [{case['case_id']}] {case['case_title']} — {case['age_days']}d | {case['priority']}")

    print()

    # Step 3: Build HTML drafts
    print("[3/4] Building HTML email drafts...")
    drafts = build_drafts(owners, filter_owner=args.owner)
    print(f"  {len(drafts)} draft(s) saved to /output/drafts/\n")

    # Step 4: Send (or skip in dry-run)
    log = init_log()
    if args.send:
        print("[4/4] Sending emails...")
        results = send_emails(drafts, owners, log, filter_owner=args.owner)
    else:
        print("[4/4] DRY RUN — emails not sent. Pass --send to deliver.\n")
        results = []

    print_summary(owners, drafts, results, dry_run=not args.send)


if __name__ == "__main__":
    main()
