=== FILENAME: dex_digest.py ===
import smtplib
import ssl
from email.message import EmailMessage
import markdown
import os
from datetime import datetime

# Configuration - update these before running
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SENDER_EMAIL = "your.email@gmail.com"  # Replace with Dex's Gmail address
SENDER_PASSWORD = "your_app_password"  # Use an app password, not your main password
RECEIVER_EMAIL = "your.email@gmail.com"  # Can be the same as sender or another email

COMMIT_FILE = "COMMIT.md"
SPARK_FILE = "SPARK.md"

def read_markdown_file(filename):
    if not os.path.exists(filename):
        return ""
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()

def convert_md_to_plaintext(md_text):
    # Convert markdown to html, then strip tags to get plaintext
    # Here we do a simple conversion by removing markdown syntax for simplicity
    # For better formatting, we use markdown to html and then strip tags
    html = markdown.markdown(md_text)
    # Strip HTML tags to get plain text
    from io import StringIO
    from html.parser import HTMLParser

    class MLStripper(HTMLParser):
        def __init__(self):
            super().__init__()
            self.reset()
            self.strict = False
            self.convert_charrefs= True
            self.text = StringIO()
        def handle_data(self, d):
            self.text.write(d)
        def get_data(self):
            return self.text.getvalue()

    s = MLStripper()
    s.feed(html)
    return s.get_data()

def build_email_body(commit_md, spark_md):
    # Compose the digest email body in plain text
    commit_text = convert_md_to_plaintext(commit_md).strip()
    spark_text = convert_md_to_plaintext(spark_md).strip()

    # For upcoming priorities, we can parse from COMMIT.md or leave blank if none
    # Here, we assume upcoming priorities are listed under a heading "Upcoming Priorities" in COMMIT.md
    upcoming_priorities = ""
    lines = commit_md.splitlines()
    capture = False
    priorities_lines = []
    for line in lines:
        if line.strip().lower().startswith("## upcoming priorities"):
            capture = True
            continue
        if capture:
            if line.startswith("#"):
                break
            priorities_lines.append(line)
    if priorities_lines:
        upcoming_priorities = convert_md_to_plaintext("\n".join(priorities_lines)).strip()

    date_str = datetime.now().strftime("%A, %B %d, %Y")

    body = f"""Dex Digest - Weekly Summary for {date_str}

Open Commitments:
{commit_text if commit_text else 'No open commitments found.'}

Recent Sparks:
{spark_text if spark_text else 'No recent sparks found.'}

Upcoming Priorities:
{upcoming_priorities if upcoming_priorities else 'No upcoming priorities found.'}

Have a productive week ahead!

-- Dex Digest Bot
"""
    return body

def send_email(subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)

def main():
    commit_md = read_markdown_file(COMMIT_FILE)
    spark_md = read_markdown_file(SPARK_FILE)

    subject = "Dex Digest - Weekly Summary"
    body = build_email_body(commit_md, spark_md)

    send_email(subject, body)
    print("Dex Digest email sent successfully.")

if __name__ == "__main__":
    main()

=== END ===

=== FILENAME: README.md ===
Dex Digest is a simple Python script that reads weekly summaries from COMMIT.md and SPARK.md files, formats a concise digest email, and sends it via Gmail SMTP. This provides a clear snapshot of open commitments, recent sparks, and upcoming priorities every Sunday to reduce mental overhead.

To use it:
1. Place your COMMIT.md and SPARK.md files in the same folder as dex_digest.py.
2. Edit dex_digest.py to set your Gmail address and an app password (generate one in your Google account security settings).
3. Run the script with: python dex_digest.py
4. To automate weekly sending, schedule this script with your OS scheduler (e.g., cron on Linux/macOS or Task Scheduler on Windows) to run every Sunday.

Make sure Python 3 is installed. No extra packages are required beyond the standard library and 'markdown' which you can install via: pip install markdown

=== END ===