import smtplib
import json
import os
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def load_markdown_section(filename):
    if not os.path.isfile(filename):
        return None
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read().strip()
        return content if content else None
    return None

def parse_commitments(md_text):
    # We expect COMMIT.md to contain open tasks, possibly as markdown lists.
    # We'll just return the raw markdown text for simplicity.
    return md_text

def parse_floats(md_text):
    # Similar for floats
    return md_text

def parse_sparks(md_text):
    # Similar for sparks
    return md_text

def build_email_body(commitments, floats, sparks):
    # Compose a simple HTML email with sections
    html = """<html>
    <head>
      <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.5; }}
        h2 {{ color: #2a7ae2; }}
        pre {{ background: #f4f4f4; padding: 10px; border-radius: 5px; white-space: pre-wrap; }}
      </style>
    </head>
    <body>
      <h1>Dex Digest Weekly Update</h1>
    """

    if commitments:
        html += "<h2>Open Commitments</h2>\n"
        html += f"<pre>{commitments}</pre>\n"
    else:
        html += "<h2>Open Commitments</h2>\n<p><em>No open commitments found.</em></p>"

    if floats:
        html += "<h2>Recent Floats</h2>\n"
        html += f"<pre>{floats}</pre>\n"
    else:
        html += "<h2>Recent Floats</h2>\n<p><em>No recent floats found.</em></p>"

    if sparks:
        html += "<h2>Upcoming Priorities (Sparks)</h2>\n"
        html += f"<pre>{sparks}</pre>\n"
    else:
        html += "<h2>Upcoming Priorities (Sparks)</h2>\n<p><em>No upcoming priorities found.</em></p>"

    html += """
    <p style="font-size:small; color:#666;">This is an automated weekly digest to keep you aligned.</p>
    </body>
    </html>
    """
    return html

def send_email(smtp_server, smtp_port, email_from, email_password, email_to, subject, html_body):
    msg = MIMEMultipart('alternative')
    msg['From'] = email_from
    msg['To'] = email_to
    msg['Subject'] = subject

    part = MIMEText(html_body, 'html')
    msg.attach(part)

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_from, email_password)
        server.sendmail(email_from, email_to, msg.as_string())
        server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def main():
    # Load config
    config_path = "config.json"
    if not os.path.isfile(config_path):
        print("Missing config.json file with SMTP/email settings.")
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    commitments_md = load_markdown_section("COMMIT.md")
    floats_md = load_markdown_section("FLOAT.md")
    sparks_md = load_markdown_section("SPARK.md")

    commitments = parse_commitments(commitments_md) if commitments_md else None
    floats = parse_floats(floats_md) if floats_md else None
    sparks = parse_sparks(sparks_md) if sparks_md else None

    email_body = build_email_body(commitments, floats, sparks)

    send_email(
        smtp_server=config.get("smtp_server"),
        smtp_port=config.get("smtp_port"),
        email_from=config.get("email_from"),
        email_password=config.get("email_password"),
        email_to=config.get("email_to"),
        subject=config.get("email_subject"),
        html_body=email_body
    )

if __name__ == "__main__":
    main()