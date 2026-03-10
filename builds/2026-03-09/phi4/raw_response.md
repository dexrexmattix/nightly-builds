```markdown
=== README.md ===

This script generates a weekly "Dex Digest" email summarizing open commitments from `COMMIT.md`, sparks from `SPARK.md`, and upcoming events from Google Calendar. It compiles this information into a clean markdown format and sends it via SMTP every Sunday morning. To run the script, ensure you have Python installed along with the required libraries (`requests`, `markdown2`, `google-auth`, `google-api-python-client`). Set up your Google API credentials and email settings in the script before running it.

=== END ===

=== dex_digest.py ===
```python
import os
import smtplib
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import requests
import markdown2
from datetime import datetime, timedelta

# Google Calendar API setup
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

def get_calendar_events():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)

    now = datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    return events_result.get('items', [])

def read_md_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def send_email(subject, body, to_email, smtp_server, smtp_port, login, password):
    msg = MIMEText(body, 'html')
    msg['Subject'] = subject
    msg['From'] = login
    msg['To'] = to_email

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(login, password)
        server.sendmail(login, [to_email], msg.as_string())

def main():
    # Read markdown files
    commit_md = read_md_file('COMMIT.md')
    spark_md = read_md_file('SPARK.md')

    # Convert markdown to HTML
    commit_html = markdown2.markdown(commit_md)
    spark_html = markdown2.markdown(spark_md)

    # Get calendar events
    events = get_calendar_events()
    event_descriptions = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        summary = event.get('summary', 'No Title')
        event_descriptions.append(f"{summary} on {start}")

    # Compile email content
    email_subject = "Dex Digest - Weekly Summary"
    email_body = f"""
    <h1>Dex Digest</h1>
    <h2>Open Commitments</h2>
    {commit_html}
    
    <h2>Sparks</h2>
    {spark_html}

    <h2>Upcoming Events</h2>
    <ul>
        {''.join(f'<li>{desc}</li>' for desc in event_descriptions)}
    </ul>
    """

    # Email settings
    to_email = 'dex@example.com'
    smtp_server = 'smtp.example.com'
    smtp_port = 587
    login = 'your-email@example.com'
    password = 'your-password'

    send_email(email_subject, email_body, to_email, smtp_server, smtp_port, login, password)

if __name__ == '__main__':
    # Run only on Sunday morning
    if datetime.today().weekday() == 6 and datetime.now().hour < 12:
        main()
```
=== END ===

```markdown
=== COMMIT.md ===
# Open Commitments

- Complete the project proposal by next Friday.
- Review the latest sprint feedback with the team.

=== END ===

=== SPARK.md ===
# Sparks of Inspiration

- Explore new design patterns for the upcoming module.
- Consider integrating AI features into our product roadmap.

=== END ===
```