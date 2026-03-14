import os
import smtplib
import ssl
from email.message import EmailMessage
from datetime import datetime, timedelta
import re

# Config - update these before running
GMAIL_USER = os.environ.get("DEX_GMAIL_USER")  # your gmail address
GMAIL_APP_PASSWORD = os.environ.get("DEX_GMAIL_APP_PASSWORD")  # app password for gmail (not your normal password)
TO_EMAIL = os.environ.get("DEX_TO_EMAIL", GMAIL_USER)  # recipient email, default to sender

# File names
COMMIT_FILE = "COMMIT.md"
SPARK_FILE = "SPARK.md"
TASK_FILE = "TASKS.md"

def read_file(filename):
    if not os.path.isfile(filename):
        return ""
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()

def extract_section(md_text, section_title):
    """
    Extracts the markdown section starting with a header matching section_title (case insensitive).
    Returns the text under that header until the next header of same or higher level.
    """
    lines = md_text.splitlines()
    pattern = re.compile(r"^(#+)\s+" + re.escape(section_title) + r"\s*$", re.IGNORECASE)
    start_idx = None
    header_level = None
    for i, line in enumerate(lines):
        m = pattern.match(line)
        if m:
            start_idx = i + 1
            header_level = len(m.group(1))
            break
    if start_idx is None:
        return ""
    content_lines = []
    for line in lines[start_idx:]:
        if re.match(r"^#{1," + str(header_level) + r"}\s", line):
            break
        content_lines.append(line)
    return "\n".join(content_lines).strip()

def parse_tasks(md_text):
    """
    Parses TASKS.md for tasks with due dates.
    Expected format:
    - [ ] Task description (due YYYY-MM-DD)
    or
    - [x] Task description (due YYYY-MM-DD)
    Returns list of dicts: {desc, due_date (datetime), done (bool)}
    """
    tasks = []
    for line in md_text.splitlines():
        line = line.strip()
        m = re.match(r"^- \[( |x)\] (.+?) \(due (\d{4}-\d{2}-\d{2})\)", line)
        if m:
            done = (m.group(1) == "x")
            desc = m.group(2).strip()
            try:
                due_date = datetime.strptime(m.group(3), "%Y-%m-%d").date()
            except ValueError:
                continue
            tasks.append({"desc": desc, "due": due_date, "done": done})
    return tasks

def filter_tasks_for_week(tasks, start_date, end_date):
    """
    Filters tasks due between start_date and end_date inclusive, and not done.
    """
    filtered = [t for t in tasks if (start_date <= t["due"] <= end_date) and not t["done"]]
    return filtered

def build_email_body(commit_text, spark_text, tasks):
    lines = []
    lines.append("Dex Digest - Weekly Summary\n")
    lines.append("Open Commitments:\n")
    if commit_text:
        lines.append(commit_text)
    else:
        lines.append("No open commitments found.")
    lines.append("\nKey Sparks:\n")
    if spark_text:
        lines.append(spark_text)
    else:
        lines.append("No key sparks found.")
    lines.append("\nUpcoming Priorities This Week:\n")
    if tasks:
        for t in tasks:
            lines.append(f"- {t['desc']} (due {t['due'].isoformat()})")
    else:
        lines.append("No upcoming priorities this week.")
    return "\n".join(lines)

def send_email(subject, body, from_addr, to_addr, password):
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(from_addr, password)
        server.send_message(msg)

def main():
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        print("ERROR: Please set environment variables DEX_GMAIL_USER and DEX_GMAIL_APP_PASSWORD before running.")
        return

    commit_md = read_file(COMMIT_FILE)
    spark_md = read_file(SPARK_FILE)
    task_md = read_file(TASK_FILE)

    # Extract whole content (no subsections) for COMMIT.md and SPARK.md
    # If you want to extract a specific section, uncomment and adjust:
    #commit_text = extract_section(commit_md, "Open Commitments") or commit_md.strip()
    #spark_text = extract_section(spark_md, "Key Sparks") or spark_md.strip()
    commit_text = commit_md.strip()
    spark_text = spark_md.strip()

    tasks = parse_tasks(task_md)

    today = datetime.today().date()
    # Next Sunday morning: if today is Sunday, send for this week (Sunday to Saturday)
    # Define week as Sunday to Saturday
    # Find last Sunday:
    last_sunday = today - timedelta(days=today.weekday()+1 if today.weekday() < 6 else 0)
    # Actually, weekday() Monday=0 ... Sunday=6, so Sunday is 6
    # We want Sunday as start of week:
    # Let's define Sunday as 6:
    # To get last Sunday:
    days_since_sunday = (today.weekday() + 1) % 7
    last_sunday = today - timedelta(days=days_since_sunday)
    next_saturday = last_sunday + timedelta(days=6)

    week_start = last_sunday
    week_end = next_saturday

    upcoming_tasks = filter_tasks_for_week(tasks, week_start, week_end)

    email_body = build_email_body(commit_text, spark_text, upcoming_tasks)
    subject = f"Dex Digest for week {week_start.isoformat()} to {week_end.isoformat()}"

    try:
        send_email(subject, email_body, GMAIL_USER, TO_EMAIL, GMAIL_APP_PASSWORD)
        print("Dex Digest email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    main()