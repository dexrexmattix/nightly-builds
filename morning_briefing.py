import re
#!/usr/bin/env python3
"""
Dex Morning Briefing — Daily email Mon-Fri + Sunday
From: askdex.rex@gmail.com → To: cwmattix@gmail.com
No LLM needed — pure script.
"""

import os
import smtplib
import ssl
import urllib.request
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import sys

# ── Config ────────────────────────────────────────────────────────────────────
SMTP_SERVER     = "smtp.gmail.com"
SMTP_PORT       = 465
SENDER_EMAIL    = "askdex.rex@gmail.com"
SENDER_PASSWORD = "nvkoarjyucdtrkbe"
RECIPIENT_EMAIL = "cwmattix@gmail.com"
WORKSPACE       = os.path.expanduser("~/.openclaw/workspace")

# ── Weather ───────────────────────────────────────────────────────────────────
def get_weather():
    try:
        url = "https://wttr.in/GrandRapids,MI?format=j1"
        req = urllib.request.Request(url, headers={"User-Agent": "curl/7.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        current = data["current_condition"][0]
        temp_f  = current["temp_F"]
        desc    = current["weatherDesc"][0]["value"]
        feels   = current["FeelsLikeF"]
        humidity = current["humidity"]
        # Pick emoji
        desc_lower = desc.lower()
        if "sun" in desc_lower or "clear" in desc_lower:
            icon = "☀️"
        elif "cloud" in desc_lower and "partly" in desc_lower:
            icon = "⛅️"
        elif "cloud" in desc_lower or "overcast" in desc_lower:
            icon = "☁️"
        elif "rain" in desc_lower or "drizzle" in desc_lower:
            icon = "🌧"
        elif "snow" in desc_lower:
            icon = "❄️"
        elif "thunder" in desc_lower or "storm" in desc_lower:
            icon = "⛈"
        elif "fog" in desc_lower or "mist" in desc_lower:
            icon = "🌫"
        else:
            icon = "🌡"
        return f"{icon} {temp_f}°F · {desc} · Feels like {feels}°F · Humidity {humidity}%"
    except Exception as e:
        return f"⚠️ Weather unavailable ({e})"

# ── File reader ───────────────────────────────────────────────────────────────
def md(text):
    """Convert inline markdown to HTML."""
    import re
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*',     r'<em>\1</em>', text)
    text = re.sub(r'`(.+?)`',       r'<code style="background:#1e1e2a;padding:1px 5px;border-radius:3px;font-size:11px;">\1</code>', text)
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2" style="color:#5b9cf6;">\1</a>', text)
    return text

def parse_tables(lines):
    """Convert markdown table lines into HTML tables, pass other lines through unchanged."""
    result = []
    i = 0
    while i < len(lines):
        raw = lines[i].rstrip()
        # Detect table start: line with pipes, followed by separator line
        if re.match(r'^\s*\|', raw) and i + 1 < len(lines) and re.match(r'^\s*\|[-:| ]+\|', lines[i+1]):
            # Parse header
            headers = [c.strip() for c in raw.strip('|').split('|')]
            i += 2  # skip separator
            # Parse rows
            rows = []
            while i < len(lines) and re.match(r'^\s*\|', lines[i]):
                cols = [c.strip() for c in lines[i].rstrip().strip('|').split('|')]
                rows.append(cols)
                i += 1
            # Build HTML table
            th_html = ''.join(f'<th style="padding:8px 12px;text-align:left;color:#aaa;font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;border-bottom:1px solid #2a2a3a;">{md(h)}</th>' for h in headers)
            rows_html = ''
            for ri, row in enumerate(rows):
                bg = '#1a1a1f' if ri % 2 == 0 else '#13131a'
                td_html = ''.join(f'<td style="padding:7px 12px;color:#ccc;font-size:13px;border-bottom:1px solid #1e1e2a;">{md(c)}</td>' for c in row)
                rows_html += f'<tr style="background:{bg};">{td_html}</tr>'
            table = f'''<div style="overflow-x:auto;margin:10px 0;"><table style="width:100%;border-collapse:collapse;border-radius:8px;overflow:hidden;border:1px solid #2a2a3a;"><thead><tr style="background:#1e1e2a;">{th_html}</tr></thead><tbody>{rows_html}</tbody></table></div>'''
            result.append(("TABLE", table))
        else:
            result.append(("LINE", raw))
            i += 1
    return result



def read_section(filename, max_lines=50, open_only=False):
    path = os.path.join(WORKSPACE, filename)
    if not os.path.isfile(path):
        return f"<em>({filename} not found)</em>"
    with open(path, "r", encoding="utf-8") as f:
        all_lines = f.readlines()

    # Filter for open_only
    filtered = []
    in_open = not open_only
    for line in all_lines[:max_lines]:
        raw = line.rstrip()
        if open_only:
            if "## 🔴 Open" in raw or "## Open" in raw:
                in_open = True
                continue
            if raw.startswith("## ") and in_open and "Open" not in raw:
                in_open = False
            if not in_open:
                continue
        filtered.append(raw)

    # Run table parser first
    parsed = parse_tables(filtered)

    html = ""
    for kind, raw in parsed:
        if kind == "TABLE":
            html += raw
            continue
        if raw.startswith("## "):
            html += f"<h3 style='color:#e07b54;margin:16px 0 6px;font-size:14px;'>{md(raw[3:])}</h3>\n"
        elif raw.startswith("### "):
            html += f"<h4 style='color:#aaa;margin:10px 0 4px;font-size:13px;'>{md(raw[4:])}</h4>\n"
        elif raw.startswith("- [ ]"):
            html += f"<div style='margin:5px 0;padding:4px 8px;background:#1a1a2a;border-radius:4px;'>☐ {md(raw[6:])}</div>\n"
        elif raw.startswith("- [x]"):
            html += f"<div style='margin:3px 0;color:#444;font-size:12px;text-decoration:line-through;'>✓ {md(raw[6:])}</div>\n"
        elif raw.startswith("- "):
            html += f"<div style='margin:4px 0;'>• {md(raw[2:])}</div>\n"
        elif raw.startswith("#"):
            pass
        elif raw.strip() == "---":
            html += "<hr style='border:none;border-top:1px solid #2a2a3a;margin:12px 0;'>\n"
        elif raw == "":
            html += "<div style='height:6px;'></div>\n"
        else:
            html += f"<div style='margin:2px 0;color:#bbb;'>{md(raw)}</div>\n"
    return html or "<em>(nothing here)</em>"

# ── Reminders ─────────────────────────────────────────────────────────────────
def get_reminders():
    path = os.path.join(WORKSPACE, "PERSONALSTATE.md")
    if not os.path.isfile(path):
        return "<em>(no reminders)</em>"
    html = ""
    in_reminders = False
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            raw = line.rstrip()
            if "## 📅 Reminders" in raw:
                in_reminders = True
                continue
            if in_reminders and raw.startswith("## "):
                break
            if in_reminders and raw.startswith("- **"):
                html += f"<div style='margin:5px 0;padding:6px 10px;background:#1a2a1a;border-radius:4px;border-left:3px solid #4caf50;'>{raw[2:]}</div>\n"
            elif in_reminders and raw.startswith("- "):
                html += f"<div style='margin:4px 0;'>• {raw[2:]}</div>\n"
    return html or "<em>(no reminders)</em>"

# ── Build HTML ─────────────────────────────────────────────────────────────────
def build_html():
    now      = datetime.now()
    day_name = now.strftime("%A")
    date_str = now.strftime("%B %d, %Y")
    weather  = get_weather()

    # Greeting by day
    greetings = {
        "Monday":    "New week, new W. Let's go 💪",
        "Tuesday":   "Tuesday — still early, still winnable.",
        "Wednesday": "Hump day. Keep the momentum.",
        "Thursday":  "Almost there. Finish strong.",
        "Friday":    "Friday. Make it count before the weekend.",
        "Saturday":  "Weekend mode. Recharge.",
        "Sunday":    "Sunday. Set the week up right."
    }
    greeting = greetings.get(day_name, "Let's get it.")

    work_html     = read_section("WORKSTATE.md", max_lines=60)
    commit_html   = read_section("COMMIT.md", open_only=True)
    reminder_html = get_reminders()

    def card(title, color, content):
        return f"""
        <div style="background:#1a1a1f;border-radius:10px;padding:18px 20px;margin-bottom:16px;border-left:4px solid {color};">
            <div style="font-size:12px;font-weight:700;color:{color};text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;">{title}</div>
            <div style="color:#ccc;font-size:13px;line-height:1.7;">{content}</div>
        </div>"""

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#0d0d0f;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
<div style="max-width:640px;margin:0 auto;padding:28px 16px;">

  <!-- Header -->
  <div style="text-align:center;margin-bottom:24px;">
    <div style="font-size:28px;">🦾</div>
    <h1 style="color:#fff;font-size:22px;margin:6px 0 2px;">Good morning, Codi</h1>
    <p style="color:#555;font-size:13px;margin:0 0 6px;">{day_name} · {date_str}</p>
    <p style="color:#888;font-size:13px;margin:0;">{greeting}</p>
  </div>

  <!-- Weather -->
  <div style="background:#13131a;border-radius:10px;padding:14px 18px;margin-bottom:16px;text-align:center;border:1px solid #1e1e2a;">
    <div style="color:#5b9cf6;font-size:14px;">📍 Grand Rapids, MI</div>
    <div style="color:#fff;font-size:16px;margin-top:4px;">{weather}</div>
  </div>

  {card("💼 Work Zone — Active Priorities", "#e07b54", work_html)}
  {card("✅ Open Commitments", "#4caf50", commit_html)}
  {card("🔔 Reminders", "#a78bfa", reminder_html)}

  <!-- Footer -->
  <div style="text-align:center;margin-top:24px;padding-top:16px;border-top:1px solid #1e1e2a;">
    <p style="color:#333;font-size:11px;margin:0;">Dex · askdex.rex@gmail.com · No LLMs were harmed in the making of this email</p>
  </div>

</div>
</body>
</html>"""

# ── Send ──────────────────────────────────────────────────────────────────────
def send_briefing(force=False):
    today = datetime.today().weekday()
    # Mon=0 ... Fri=4, skip Sat=5
    if today == 5 and not force:
        print("Saturday — no briefing. Run with --force to override.")
        sys.exit(0)

    print("Building morning briefing...")
    html_body = build_html()

    now = datetime.now()
    msg = MIMEMultipart("alternative")
    msg["From"]    = f"Dex 🦾 <{SENDER_EMAIL}>"
    msg["To"]      = RECIPIENT_EMAIL
    msg["Subject"] = f"☀️ Morning Brief — {now.strftime('%A, %B %d')}"
    msg.attach(MIMEText(html_body, "html"))

    context = ssl.create_default_context()
    print(f"Sending to {RECIPIENT_EMAIL}...")
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())

    print("✅ Morning briefing sent.")

if __name__ == "__main__":
    force = "--force" in sys.argv
    send_briefing(force=force)
