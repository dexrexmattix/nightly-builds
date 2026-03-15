=== FILENAME: README.md ===
This Python script compiles key points from FLOAT.md, SPARK.md, and COMMIT.md files into a clean, concise Sunday "Dex Digest" email summarizing key floats, sparks, and open commitments for the upcoming week. It then sends the digest via SMTP using your Gmail account. To run it, place your markdown files in the same folder, update the sender, recipient, and Gmail app password in the script, and run `python dex_digest.py` from the terminal.

=== END ===

=== FILENAME: dex_digest.py ===
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

def read_markdown_section(filename):
    if not os.path.isfile(filename):
        return f"*No {filename} file found.*"
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read().strip()
        if not content:
            return f"*{filename} is empty.*"
        return content

def create_email_body(floats, sparks, commits):
    html = f"""
    <html>
    <head>
      <style>
        body {{
          font-family: Arial, sans-serif;
          line-height: 1.5;
          color: #333;
        }}
        h2 {{
          color: #2a7ae2;
          border-bottom: 2px solid #2a7ae2;
          padding-bottom: 4px;
        }}
        pre {{
          background: #f4f4f4;
          padding: 10px;
          border-radius: 4px;
          white-space: pre-wrap;
          font-family: Consolas, monospace;
        }}
      </style>
    </head>
    <body>
      <h1>Sunday Dex Digest</h1>
      <p>Here is your summary of key floats, sparks, and open commitments for the upcoming week.</p>
      <h2>Floats</h2>
      <pre>{floats}</pre>
      <h2>Sparks</h2>
      <pre>{sparks}</pre>
      <h2>Open Commitments</h2>
      <pre>{commits}</pre>
      <p>Have a productive week!</p>
    </body>
    </html>
    """
    return html

def send_email(sender_email, sender_password, recipient_email, subject, html_body):
    msg = MIMEMultipart('alternative')
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    part = MIMEText(html_body, 'html')
    msg.attach(part)

    # Gmail SMTP server
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print("Failed to send email:", e)

def main():
    floats = read_markdown_section('FLOAT.md')
    sparks = read_markdown_section('SPARK.md')
    commits = read_markdown_section('COMMIT.md')

    email_body = create_email_body(floats, sparks, commits)

    # === CONFIGURE THESE ===
    sender_email = 'your.email@gmail.com'
    sender_password = 'your_gmail_app_password'
    recipient_email = 'recipient.email@example.com'
    subject = 'Sunday Dex Digest'

    send_email(sender_email, sender_password, recipient_email, subject, email_body)

if __name__ == '__main__':
    main()

=== END ===