=== FILENAME: dex_digest.py ===
import os
import smtplib
import datetime
import email.utils
from email.mime.text import MIMEText

def read_markdown_section(file_path):
    if not os.path.exists(file_path):
        return "(No data found)"
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
    if not content:
        return "(No data found)"
    return content

def read_calendar_events(file_path, from_date, to_date):
    """
    Parse a simple local calendar export in .ics format and extract events between from_date and to_date.
    Returns a list of tuples (date, summary).
    """
    if not os.path.exists(file_path):
        return []

    events = []
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    event = {}
    inside_event = False
    for line in lines:
        line = line.strip()
        if line == "BEGIN:VEVENT":
            event = {}
            inside_event = True
        elif line == "END:VEVENT":
            inside_event = False
            # Process event date and summary
            dtstart = event.get("DTSTART")
            summary = event.get("SUMMARY", "(No title)")
            if dtstart:
                # Parse date, support date or datetime in YYYYMMDD or YYYYMMDDTHHMMSSZ format
                try:
                    if "T" in dtstart:
                        dt = datetime.datetime.strptime(dtstart, "%Y%m%dT%H%M%SZ")
                    else:
                        dt = datetime.datetime.strptime(dtstart, "%Y%m%d")
                except Exception:
                    continue
                if from_date <= dt.date() <= to_date:
                    events.append((dt.date(), summary))
        elif inside_event:
            if ":" in line:
                key, val = line.split(":", 1)
                event[key] = val
    # Sort events by date
    events.sort(key=lambda x: x[0])
    return events

def format_email_body(commitments, sparks, events, from_date, to_date):
    lines = []
    lines.append(f"Dex Digest for week {from_date.strftime('%Y-%m-%d')} to {to_date.strftime('%Y-%m-%d')}")
    lines.append("="*40)
    lines.append("\nOpen Commitments:\n")
    lines.append(commitments)
    lines.append("\nSparks:\n")
    lines.append(sparks)
    lines.append("\nUpcoming Events:\n")
    if events:
        for ev_date, summary in events:
            lines.append(f"- {ev_date.strftime('%a %b %d')}: {summary}")
    else:
        lines.append("(No upcoming events)")
    lines.append("\nHave a great week!\n")
    return "\n".join(lines)

def send_email(smtp_server, smtp_port, smtp_user, smtp_password, from_addr, to_addr, subject, body):
    msg = MIMEText(body)
    msg.set_unixfrom('author')
    msg['To'] = email.utils.formataddr(('Dex', to_addr))
    msg['From'] = email.utils.formataddr(('Dex Digest', from_addr))
    msg['Subject'] = subject

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_user, smtp_password)
    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()

def main():
    # Paths to source files
    commit_path = "COMMIT.md"
    spark_path = "SPARK.md"
    calendar_path = "calendar.ics"

    # Calculate last week Sunday to this Sunday (inclusive)
    today = datetime.date.today()
    # Find most recent Sunday (including today if Sunday)
    this_sunday = today - datetime.timedelta(days=today.weekday()+1) if today.weekday() != 6 else today
    last_sunday = this_sunday - datetime.timedelta(days=7)

    # Read markdown content
    commitments = read_markdown_section(commit_path)
    sparks = read_markdown_section(spark_path)

    # Read calendar events for upcoming week (this_sunday to next Saturday)
    upcoming_start = this_sunday
    upcoming_end = this_sunday + datetime.timedelta(days=6)
    events = read_calendar_events(calendar_path, upcoming_start, upcoming_end)

    # Format email content
    subject = f"Dex Digest: Week of {upcoming_start.strftime('%b %d, %Y')}"
    body = format_email_body(commitments, sparks, events, upcoming_start, upcoming_end)

    # SMTP config from environment variables
    smtp_server = os.environ.get("SMTP_SERVER")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    from_addr = os.environ.get("FROM_EMAIL")
    to_addr = os.environ.get("TO_EMAIL")

    if not all([smtp_server, smtp_port, smtp_user, smtp_password, from_addr, to_addr]):
        print("Error: Missing SMTP or email environment variables. Please set SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, FROM_EMAIL, TO_EMAIL.")
        return

    send_email(smtp_server, smtp_port, smtp_user, smtp_password, from_addr, to_addr, subject, body)
    print("Dex Digest email sent successfully.")

if __name__ == "__main__":
    main()

=== END ===
=== FILENAME: README.md ===
Dex Digest is a simple Python script that compiles a weekly summary email every Sunday morning. It reads your open commitments from COMMIT.md, sparks from SPARK.md, and upcoming events from a local calendar export file named calendar.ics. It then sends a clean summary email via SMTP to your email address, helping you keep track of priorities without daily noise.

To use it:
1. Place your COMMIT.md, SPARK.md, and calendar.ics files in the same folder as dex_digest.py.
2. Set the following environment variables with your SMTP and email info:
   - SMTP_SERVER (e.g., smtp.gmail.com)
   - SMTP_PORT (usually 587)
   - SMTP_USER (your SMTP username/email)
   - SMTP_PASSWORD (your SMTP password or app password)
   - FROM_EMAIL (the sender email address)
   - TO_EMAIL (the recipient email address)
3. Run the script from the terminal:
   ```
   python dex_digest.py
   ```
You can schedule this script to run every Sunday morning using your OS scheduler (cron, Task Scheduler, etc.) for automatic weekly emails.

=== END ===