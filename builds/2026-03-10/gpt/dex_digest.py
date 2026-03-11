import os
import smtplib
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Configuration - update these before running
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "your.email@gmail.com"
SMTP_PASSWORD = "your_app_password_or_password"
EMAIL_FROM = "your.email@gmail.com"
EMAIL_TO = "recipient.email@example.com"
EMAIL_SUBJECT = "Dex Digest - Weekly Summary"

# Filenames to read
COMMIT_FILE = "COMMIT.md"
FLOAT_FILE = "FLOAT.md"
SPARK_FILE = "SPARK.md"
CALENDAR_FILE = "CALENDAR.md"

def read_markdown_section(filename):
    """Read the markdown file and return a list of non-empty stripped lines."""
    if not os.path.exists(filename):
        return []
    with open(filename, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines()]
    # Filter out empty lines and markdown headers if any
    filtered = [line for line in lines if line and not line.startswith("#")]
    return filtered

def read_calendar_events(filename):
    """Read calendar events from CALENDAR.md and filter for upcoming week."""
    if not os.path.exists(filename):
        return []
    events = []
    today = datetime.date.today()
    next_sunday = today + datetime.timedelta((6 - today.weekday()) % 7)
    next_saturday = next_sunday + datetime.timedelta(days=6)
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # Expect format: YYYY-MM-DD - Event description
            if " - " in line:
                date_part, desc = line.split(" - ", 1)
                try:
                    event_date = datetime.datetime.strptime(date_part.strip(), "%Y-%m-%d").date()
                    if next_sunday <= event_date <= next_saturday:
                        events.append(f"{event_date.isoformat()}: {desc.strip()}")
                except ValueError:
                    # Ignore lines with invalid date format
                    continue
    return events

def format_section(title, items):
    if not items:
        return f"### {title}\n_No items._\n"
    lines = "\n".join(f"- {item}" for item in items)
    return f"### {title}\n{lines}\n"

def create_email_body():
    commits = read_markdown_section(COMMIT_FILE)
    floats = read_markdown_section(FLOAT_FILE)
    sparks = read_markdown_section(SPARK_FILE)
    events = read_calendar_events(CALENDAR_FILE)

    body_md = f"""\
# Dex Digest - Weekly Summary

Hello Codi,

Here is your weekly Dex Digest summarizing your open commitments, floats, sparks, and upcoming priorities for the week.

{format_section("Open Commitments", commits)}
{format_section("Floats (Ideas & Notes)", floats)}
{format_section("Sparks (Inspiration & Sparks)", sparks)}
{format_section("Upcoming Calendar Events (Next Week)", events)}

Stay aligned and have a productive week ahead!

Best,
Dex Digest Bot
"""
    return body_md

def send_email(body_md):
    # Create message container
    msg = MIMEMultipart('alternative')
    msg['Subject'] = EMAIL_SUBJECT
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO

    # Plain text fallback (strip markdown)
    plain_text = body_md.replace("#", "").replace("*", "").replace("_", "")
    part1 = MIMEText(plain_text, 'plain')
    part2 = MIMEText(body_md, 'markdown')

    msg.attach(part1)
    msg.attach(part2)

    # Connect and send email
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USERNAME, SMTP_PASSWORD)
    server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
    server.quit()

def main():
    today = datetime.date.today()
    # Only send on Sunday morning
    if today.weekday() != 6:
        print("Today is not Sunday. Dex Digest will only send on Sundays.")
        return

    print("Creating Dex Digest email...")
    body = create_email_body()
    print("Sending email...")
    send_email(body)
    print("Dex Digest sent successfully.")

if __name__ == "__main__":
    main()