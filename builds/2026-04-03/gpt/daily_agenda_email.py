import os
import smtplib
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from google.oauth2 import service_account
from googleapiclient.discovery import build
import gspread

# === CONFIGURATION ===
# Google API service account JSON file path
SERVICE_ACCOUNT_FILE = 'credentials.json'

# Google Calendar ID (usually your email)
CALENDAR_ID = 'primary'

# Google Sheet ID containing to-dos (must be shared with service account email)
TODO_SHEET_ID = 'YOUR_GOOGLE_SHEET_ID_HERE'

# Email settings
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_SENDER = 'your_email@gmail.com'
EMAIL_PASSWORD = 'your_email_app_password'  # Use app password if 2FA enabled
EMAIL_RECEIVER = 'your_email@gmail.com'  # Can be same as sender or different

# === END CONFIGURATION ===

def get_google_services():
    scopes = [
        'https://www.googleapis.com/auth/calendar.readonly',
        'https://www.googleapis.com/auth/spreadsheets.readonly',
    ]
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=scopes)
    calendar_service = build('calendar', 'v3', credentials=creds)
    gc = gspread.authorize(creds)
    return calendar_service, gc

def get_todays_events(calendar_service):
    now = datetime.datetime.utcnow()
    start_of_day = datetime.datetime.combine(now.date(), datetime.time.min).isoformat() + 'Z'
    end_of_day = datetime.datetime.combine(now.date(), datetime.time.max).isoformat() + 'Z'

    events_result = calendar_service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=start_of_day,
        timeMax=end_of_day,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])
    return events

def get_todos(gc):
    sheet = gc.open_by_key(TODO_SHEET_ID).sheet1
    # Assume first row is header, columns: Task | Status
    records = sheet.get_all_records()
    # Filter only incomplete tasks (Status != 'Done' or empty)
    todos = [r['Task'] for r in records if r.get('Status', '').strip().lower() != 'done']
    return todos

def format_email(events, todos):
    today_str = datetime.datetime.now().strftime('%A, %B %d, %Y')
    email_html = f"<h2>Daily Agenda for {today_str}</h2>"

    email_html += "<h3>Today's Events:</h3>"
    if not events:
        email_html += "<p>No events scheduled for today.</p>"
    else:
        email_html += "<ul>"
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            # Format start time nicely
            try:
                dt = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
                start_str = dt.strftime('%I:%M %p').lstrip('0')
            except Exception:
                start_str = start
            summary = event.get('summary', 'No Title')
            email_html += f"<li><b>{start_str}</b>: {summary}</li>"
        email_html += "</ul>"

    email_html += "<h3>To-Do List:</h3>"
    if not todos:
        email_html += "<p>No pending tasks. Great job!</p>"
    else:
        email_html += "<ul>"
        for task in todos:
            email_html += f"<li>{task}</li>"
        email_html += "</ul>"

    email_html += "<p>Have a productive day!</p>"
    return email_html

def send_email(subject, html_content):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER

    part = MIMEText(html_content, 'html')
    msg.attach(part)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())

def main():
    calendar_service, gc = get_google_services()
    events = get_todays_events(calendar_service)
    todos = get_todos(gc)
    email_content = format_email(events, todos)
    subject = f"Your Daily Agenda for {datetime.datetime.now().strftime('%B %d, %Y')}"
    send_email(subject, email_content)
    print("Daily agenda email sent successfully.")

if __name__ == '__main__':
    main()