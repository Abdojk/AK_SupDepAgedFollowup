"""
email_sender.py — Send HTML emails via SMTP (Office 365 / Gmail).
Falls back to Microsoft Graph API if GRAPH_* env vars are set.
"""

import os
import smtplib
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

MANAGER_EMAIL = os.getenv("MANAGER_EMAIL", "")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.office365.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# Graph API (optional)
GRAPH_TENANT_ID = os.getenv("GRAPH_TENANT_ID", "")
GRAPH_CLIENT_ID = os.getenv("GRAPH_CLIENT_ID", "")
GRAPH_CLIENT_SECRET = os.getenv("GRAPH_CLIENT_SECRET", "")

USE_GRAPH = all([GRAPH_TENANT_ID, GRAPH_CLIENT_ID, GRAPH_CLIENT_SECRET])


def send_emails(drafts: dict, owners: dict, log: list, filter_owner: str = None) -> list:
    """Send one email per owner (to owner, CC manager)."""
    results = []

    for owner_email, draft in drafts.items():
        if filter_owner and owner_email != filter_owner:
            continue

        owner_name = owners[owner_email]["owner_name"]
        subject = draft["subject"]
        html = draft["html_content"]

        try:
            if USE_GRAPH:
                _send_via_graph(owner_email, owner_name, subject, html)
            else:
                _send_via_smtp(owner_email, owner_name, subject, html)

            status = "SENT"
            print(f"  ✓ Email sent to {owner_name} <{owner_email}>")
        except Exception as e:
            status = f"FAILED: {e}"
            print(f"  ✗ Failed to send to {owner_email}: {e}")

        results.append({"owner_email": owner_email, "status": status})
        log.append({"owner_email": owner_email, "subject": subject, "status": status})

    _write_log(log)
    return results


def _send_via_smtp(to_email: str, to_name: str, subject: str, html: str):
    """Send via SMTP — TO: owner + manager (both primary recipients)."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    # Both owner and manager are primary TO recipients
    msg["To"] = f"{to_name} <{to_email}>, {MANAGER_EMAIL}"

    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, [to_email, MANAGER_EMAIL], msg.as_string())


def _send_via_graph(to_email: str, to_name: str, subject: str, html: str):
    """Send via Microsoft Graph API using client credentials."""
    token = _get_graph_token()
    endpoint = f"https://graph.microsoft.com/v1.0/users/{SMTP_USER}/sendMail"

    payload = {
        "message": {
            "subject": subject,
            "body": {"contentType": "HTML", "content": html},
            "toRecipients": [
                {"emailAddress": {"address": to_email, "name": to_name}},
                {"emailAddress": {"address": MANAGER_EMAIL, "name": "Abdo"}},
            ],
        },
        "saveToSentItems": True,
    }

    response = requests.post(
        endpoint,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=payload,
    )

    if response.status_code not in (200, 202):
        raise Exception(f"Graph API error {response.status_code}: {response.text}")


def _get_graph_token() -> str:
    """Fetch OAuth2 token from Azure AD."""
    url = f"https://login.microsoftonline.com/{GRAPH_TENANT_ID}/oauth2/v2.0/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": GRAPH_CLIENT_ID,
        "client_secret": GRAPH_CLIENT_SECRET,
        "scope": "https://graph.microsoft.com/.default",
    }
    resp = requests.post(url, data=data)
    resp.raise_for_status()
    return resp.json()["access_token"]


def _write_log(log: list):
    """Append results to output/send_log.csv."""
    import csv
    from pathlib import Path

    log_path = Path("output/send_log.csv")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = log_path.exists()

    with open(log_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["owner_email", "subject", "status"])
        if not file_exists:
            writer.writeheader()
        writer.writerows(log)
