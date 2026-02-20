# CRM Case Follow-Up Email Automation

## Project Overview
Automated follow-up email system for aged CRM support/development cases. Reads open cases from a CSV export, groups by owner, and sends HTML follow-up emails highlighting the top 3 oldest cases per team member.

## Key Configuration
- **Manager**: Abdo Khoury (Akhoury@info-sys.com)
- **Domain**: info-sys.com
- **Email pattern**: FirstInitial+LastName@info-sys.com
- **Manager cases**: Excluded from email sends (no self-email)
- **Email routing**: Every email goes TO: case owner AND TO: Akhoury@info-sys.com

## Owner Email Map
| Owner | Email |
|---|---|
| Fadi Hanna | FHanna@info-sys.com |
| Georges Mouaikel | GMouaikel@info-sys.com |
| Jana Sweid | JSweid@info-sys.com |
| Mennatullah El Bahr | MElBahr@info-sys.com |
| Raji Aoun | RAoun@info-sys.com |
| Rebecca Estephan | REstephan@info-sys.com |

## Running
```bash
# Dry-run (default) — loads data, prints summary, saves drafts, no emails sent
python main.py

# Live send — actually delivers emails via SMTP/Graph API
python main.py --send

# Filter to a single owner
python main.py --owner FHanna@info-sys.com
```

## Project Structure
```
main.py                  # Entry point (--send flag toggles live mode)
src/
  parser.py              # CSV loading, column mapping, schema validation
  grouper.py             # Group cases by owner, extract top 3 oldest
  email_builder.py       # Jinja2 HTML email draft generation
  email_sender.py        # SMTP / Microsoft Graph email delivery
  logger.py              # Session logging and summary output
data/
  cases.csv              # Input: CRM case export (177 rows)
templates/
  followup_email.html    # Jinja2 HTML email template
output/
  drafts/                # Generated HTML email drafts (one per owner)
  send_log.csv           # Send results log
```

## CSV Column Mapping
The CRM export uses non-standard column names. `parser.py` maps them:
| CRM Export Column | → Internal Name |
|---|---|
| `(Do Not Modify) Case` | `case_id` |
| `Case Title` | `case_title` |
| `Owner` | `owner_name` |
| `Created On` | `created_date` |
| `Priority` | `priority` |

## Dependencies
```
pip install pandas jinja2 python-dotenv requests openpyxl
```

## SMTP Configuration
Copy `.env.example` → `.env` and fill in SMTP credentials (or Microsoft Graph API keys).
