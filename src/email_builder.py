"""
email_builder.py — Build and save HTML email drafts using Jinja2.
"""

import os
from datetime import date
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv

load_dotenv()

DRAFTS_DIR = Path("output/drafts")
TEMPLATE_FILE = "followup_email.html"

MANAGER_NAME = os.getenv("MANAGER_NAME", "Abdo")
MANAGER_EMAIL = os.getenv("MANAGER_EMAIL", "Akhoury@info-sys.com")


def build_drafts(owners: dict, filter_owner: str = None) -> dict:
    """
    Build one HTML email per owner and save to /output/drafts/.
    Returns a dict: { owner_email: { "subject": ..., "html_path": ..., "html_content": ... } }
    """
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)

    env = Environment(loader=FileSystemLoader("templates"), autoescape=True)
    template = env.get_template(TEMPLATE_FILE)

    drafts = {}
    today_str = date.today().strftime("%d %B %Y")

    for owner_email, data in owners.items():
        if filter_owner and owner_email != filter_owner:
            continue

        subject = f"Action Required: Follow-Up on Your Top Aged Cases – {today_str}"

        html_content = template.render(
            owner_name=data["owner_name"],
            top3=data["top3"],
            total_cases=data["total_cases"],
            manager_name=MANAGER_NAME,
            manager_email=MANAGER_EMAIL,
            today=today_str,
        )

        # Save draft
        safe_filename = owner_email.replace("@", "_at_").replace(".", "_") + ".html"
        draft_path = DRAFTS_DIR / safe_filename
        draft_path.write_text(html_content, encoding="utf-8")

        drafts[owner_email] = {
            "subject": subject,
            "html_path": str(draft_path),
            "html_content": html_content,
        }

        print(f"  Draft saved: {draft_path}")

    return drafts
