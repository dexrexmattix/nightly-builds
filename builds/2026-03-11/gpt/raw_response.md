=== FILENAME: README.md ===
This Python script automatically generates and sends a weekly "Dex Digest" email every Sunday evening. It reads from three markdown files—SPARK.md, FLOAT.md, and COMMIT.md—summarizes their contents, and emails the summary to a specified recipient using SMTP (Gmail). To run it, configure your Gmail SMTP credentials and recipient email in the script, then schedule it to run weekly on Sunday evenings (e.g., via cron). The script handles markdown parsing and email formatting for a clean digest.

Usage:
1. Update the SMTP and email settings in the script.
2. Place SPARK.md, FLOAT.md, and COMMIT.md in the same directory.
3. Run `python dex_digest.py` manually or schedule it weekly.

=== END ===

=== FILENAME: dex_digest.py ===
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import os
import re

# CONFIGURATION - Update these before running
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SENDER_EMAIL = "your.email@gmail.com"       # Your Gmail address
SENDER_PASSWORD = "your_app_password"       # Your Gmail App Password (NOT your normal password)
RECIPIENT_EMAIL = "codi@example.com"        # Recipient email (Codi)

# Markdown files to read
FILES = {
    "Sparks": "SPARK.md",
    "Floats": "FLOAT.md",
    "Open Commitments": "COMMIT.md"
}

def read_markdown_file(filename):
    if not os.path.isfile(filename):
        return None
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()

def parse_markdown_to_list(md_text):
    """
    Parses markdown text to a list of items.
    Supports bullet points (-, *, +) and numbered lists.
    Returns a list of strings.
    """
    if not md_text:
        return []
    lines = md_text.splitlines()
    items = []
    bullet_pattern = re.compile(r'^\s*[-*+]\s+(.*)')
    number_pattern = re.compile(r'^\s*\d+\.\s+(.*)')
    for line in lines:
        bullet_match = bullet_pattern.match(line)
        number_match = number_pattern.match(line)
        if bullet_match:
            items.append(bullet_match.group(1).strip())
        elif number_match:
            items.append(number_match.group(1).strip())
    return items

def format_section(title, items):
    if not items:
        return f"<p><i>No {title.lower()} this week.</i></p>"
    html = f"<h2>{title}</h2><ul>"
    for item in items:
        html += f"<li>{item}</li>"
    html += "</ul>"
    return html

def build_email_body(sections):
    date_str = datetime.now().strftime("%B %d, %Y")
    html = f"""<html>
    <body>
    <h1>Dex Digest - Weekly Summary ({date_str})</h1>
    """
    for title, items in sections.items():
        html += format_section(title, items)
    html += """
    <p>--<br/>Automated Dex Digest</p>
    </body>
    </html>"""
    return html

def send_email(subject, html_content):
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = SENDER_EMAIL
    message["To"] = RECIPIENT_EMAIL

    part = MIMEText(html_content, "html")
    message.attach(part)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, message.as_string())

def main():
    sections = {}
    for title, filename in FILES.items():
        md_text = read_markdown_file(filename)
        items = parse_markdown_to_list(md_text)
        sections[title] = items

    email_body = build_email_body(sections)
    subject = "Dex Digest: Weekly Summary"

    try:
        send_email(subject, email_body)
        print("Dex Digest email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    main()

=== END ===