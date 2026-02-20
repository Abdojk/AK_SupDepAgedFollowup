"""
logger.py — Session logging and summary output.
"""


def init_log() -> list:
    return []


def print_summary(owners: dict, drafts: dict, results: list, dry_run: bool):
    sent = [r for r in results if r["status"] == "SENT"]
    failed = [r for r in results if r["status"] != "SENT"]

    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    print(f"  Owners processed : {len(owners)}")
    print(f"  Drafts saved     : {len(drafts)}")

    if dry_run:
        print("  Emails sent      : 0  (dry-run mode)")
        print("  → Run with --send to deliver emails.")
    else:
        print(f"  Emails sent      : {len(sent)}")
        print(f"  Failures         : {len(failed)}")
        if failed:
            for f in failed:
                print(f"    ✗ {f['owner_email']}: {f['status']}")

    print("=" * 60 + "\n")
