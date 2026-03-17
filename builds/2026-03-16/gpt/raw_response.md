=== FILENAME: dex_digest.py ===
import os
import smtplib
import ssl
from email.message import EmailMessage
from datetime import datetime
import sys

# Config: update these before running
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465  # SSL port
SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASSWORD = "your_app_password_or_email_password"
RECIPIENT_EMAIL = "recipient_email@example.com"

# Filenames to read from
FLOAT_FILE = "FLOAT.md"
SPARK_FILE = "SPARK.md"
COMMIT_FILE = "COMMIT.md"

def read_file_content(filename):
    if not os.path.isfile(filename):
        return f"*No {filename} found.*"
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if not content:
            return f"*{filename} is empty.*"
        return content

def build_email_body():
    float_content = read_file_content(FLOAT_FILE)
    spark_content = read_file_content(SPARK_FILE)
    commit_content = read_file_content(COMMIT_FILE)

    body = f"""\
Hi Codi,

Here is your weekly Dex Digest for the week of {datetime.now().strftime("%B %d, %Y")}.

--- FLOATS ---
{float_content}

--- SPARKS ---
{spark_content}

--- OPEN COMMITMENTS ---
{commit_content}

Keep up the great work!

Best,
Dex Digest Bot
"""
    return body

def send_email(subject, body):
    msg = EmailMessage()
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL
    msg["Subject"] = subject
    msg.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)

def main():
    # Check if today is Sunday
    if datetime.today().weekday() != 6:
        print("Today is not Sunday. This script is intended to run on Sundays.")
        sys.exit(0)

    subject = "Dex Digest Weekly Summary"
    body = build_email_body()
    send_email(subject, body)
    print("Dex Digest email sent successfully.")

if __name__ == "__main__":
    main()

=== END ===
=== FILENAME: README.md ===
Dex Digest is a simple Python script that compiles key points from FLOAT.md, SPARK.md, and COMMIT.md files into a concise weekly email summary. It is designed to run on Sundays and sends the digest via Gmail SMTP to help Codi stay organized with a single overview message.

To use:
1. Place your FLOAT.md, SPARK.md, and COMMIT.md files in the same folder as dex_digest.py.
2. Edit dex_digest.py to set your Gmail address, recipient email, and app password (or email password if less secure apps are allowed).
3. Run the script on a Sunday using: python dex_digest.py
4. The script will send the weekly digest email automatically.

Note: For Gmail SMTP, you may need to create an App Password if you have 2FA enabled or allow less secure apps access.

=== END ===