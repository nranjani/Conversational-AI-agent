# migrate_sheets_to_postgres.py
# One-time copy of your Google Sheet tabs into Postgres.
#
# Run locally (needs credentials.json and .env with SHEET_NAME + DATABASE_URL):
#   pip install gspread google-auth "psycopg[binary]" python-dotenv
#   python migrate_sheets_to_postgres.py            # preview only
#   python migrate_sheets_to_postgres.py --commit   # actually write
#
# Run schema.sql in your database first.

import os
import sys
from datetime import datetime

from dotenv import load_dotenv

from tools.booking_tool import parse_date_or_none
from tools.db import get_conn

load_dotenv()

COMMIT = "--commit" in sys.argv


def open_sheet():
    import gspread
    from google.oauth2.service_account import Credentials

    creds = Credentials.from_service_account_file(
        os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "credentials.json"),
        scopes=[
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ],
    )
    return gspread.authorize(creds).open(os.environ["SHEET_NAME"])


def read_tab(sheet, name):
    """Rows as lists, header row removed, fully blank rows dropped."""
    values = sheet.worksheet(name).get_all_values()
    return [r for r in values[1:] if any(c.strip() for c in r)]


def cell(row, i):
    return row[i].strip() if i < len(row) else ""


def parse_ts(text):
    for fmt in ("%Y-%m-%d %H:%M:%S", "%m/%d/%Y %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass
    return None


def build_bookings(rows):
    # Sheet columns: timestamp, pet_name, service_type, date, time,
    #                phone_number, status (col 7), updated_at (col 8)
    out, bad_dates = [], []
    for r in rows:
        date = parse_date_or_none(cell(r, 3)) if cell(r, 3) else None
        if cell(r, 3) and not date:
            bad_dates.append(cell(r, 3))
        status = cell(r, 6).lower() or "confirmed"
        if status not in ("confirmed", "cancelled", "rebooked"):
            status = "confirmed"
        out.append((
            parse_ts(cell(r, 0)) or datetime.now(),
            cell(r, 1) or "unknown",
            cell(r, 2) or "unknown",
            date,
            cell(r, 4),
            cell(r, 5),
            status,
            parse_ts(cell(r, 7)),
        ))
    return out, bad_dates


def build_faq(rows):
    # intent_name, question, answer
    return [
        (cell(r, 0), cell(r, 1), cell(r, 2))
        for r in rows if cell(r, 0) and cell(r, 2)
    ]


def build_receptionist(rows):
    # timestamp, name, phone, query
    return [
        (parse_ts(cell(r, 0)) or datetime.now(),
         cell(r, 1), cell(r, 2), cell(r, 3))
        for r in rows
    ]


def write_all(bookings, faq, receptionist):
    with get_conn() as conn:
        # Refuse to double-import
        for table in ("bookings", "faq", "receptionist_requests"):
            n = conn.execute(f"SELECT count(*) AS n FROM {table}").fetchone()["n"]
            if n:
                raise SystemExit(
                    f"Table '{table}' already has {n} rows. "
                    "Empty it first if you want to re-run the migration."
                )
        with conn.cursor() as cur:
            cur.executemany(
                """INSERT INTO bookings
                   (created_at, pet_name, service_type, booking_date,
                    booking_time, phone_number, status, updated_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                bookings,
            )
            cur.executemany(
                "INSERT INTO faq (intent_name, question, answer) VALUES (%s, %s, %s)",
                faq,
            )
            cur.executemany(
                """INSERT INTO receptionist_requests
                   (created_at, customer_name, phone_number, query_text)
                   VALUES (%s, %s, %s, %s)""",
                receptionist,
            )
    # get_conn commits all three tables together, or none if anything failed


def main(sheet=None):
    sheet = sheet or open_sheet()
    bookings, bad_dates = build_bookings(read_tab(sheet, "booking"))
    faq = build_faq(read_tab(sheet, "FAQ"))
    receptionist = build_receptionist(read_tab(sheet, "receptionist"))

    print(f"bookings:     {len(bookings)} rows")
    print(f"faq:          {len(faq)} rows")
    print(f"receptionist: {len(receptionist)} rows")
    if bad_dates:
        print(f"⚠️  {len(bad_dates)} booking dates couldn't be read and "
              f"will be stored as NULL: {sorted(set(bad_dates))}")

    if not COMMIT:
        print("\nPreview only. Re-run with --commit to write to Postgres.")
        return

    write_all(bookings, faq, receptionist)
    print("\n✅ Migration complete.")


if __name__ == "__main__":
    main()
