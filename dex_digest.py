import re
#!/usr/bin/env python3
"""
Dex Digest — Weekly Sunday summary email
From: askdex.rex@gmail.com → To: cwmattix@gmail.com
Reads: FLOAT.md, SPARK.md, COMMIT.md, PERSONALSTATE.md from workspace
"""

import os
import smtplib
import ssl
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import sys

# ── Config ────────────────────────────────────────────────────────────────────
SMTP_SERVER    = "smtp.gmail.com"
SMTP_PORT      = 465
SENDER_EMAIL   = "askdex.rex@gmail.com"
SENDER_PASSWORD = "nvkoarjyucdtrkbe"   # Gmail App Password
RECIPIENT_EMAIL = "cwmattix@gmail.com"

WORKSPACE = os.path.expanduser("~/.openclaw/workspace")

# ── Helpers ───────────────────────────────────────────────────────────────────
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



def read_file(filename, max_lines=60):
    path = os.path.join(WORKSPACE, filename)
    if not os.path.isfile(path):
        return f"<em>({filename} not found)</em>"
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    if not any(l.strip() for l in lines[:max_lines]):
        return f"<em>({filename} is empty)</em>"

    raw_lines = [l.rstrip() for l in lines[:max_lines]]
    parsed = parse_tables(raw_lines)

    html = ""
    for kind, line in parsed:
        if kind == "TABLE":
            html += line
            continue
        if line.startswith("## "):
            html += f"<h3 style='color:#e07b54;margin:16px 0 6px;'>{md(line[3:])}</h3>\n"
        elif line.startswith("### "):
            html += f"<h4 style='color:#aaa;margin:12px 0 4px;'>{md(line[4:])}</h4>\n"
        elif line.startswith("- [ ]"):
            html += f"<div style='margin:5px 0;padding:4px 8px;background:#1a1a2a;border-radius:4px;'>☐ {md(line[6:])}</div>\n"
        elif line.startswith("- [x]"):
            html += f"<div style='margin:4px 0;color:#555;text-decoration:line-through;'>✓ {md(line[6:])}</div>\n"
        elif line.startswith("- "):
            html += f"<div style='margin:4px 0;'>• {md(line[2:])}</div>\n"
        elif line.startswith("#"):
            pass
        elif line.strip() == "---":
            html += "<hr style='border:none;border-top:1px solid #2a2a3a;margin:12px 0;'>\n"
        elif line == "":
            html += "<br>\n"
        else:
            html += f"<div style='margin:2px 0;'>{md(line)}</div>\n"
    return html

def build_html():
    now = datetime.now()
    date_str = now.strftime("%A, %B %d, %Y")
    week_num = now.strftime("%U")

    float_html   = read_file("FLOAT.md")
    spark_html   = read_file("SPARK.md")
    commit_html  = read_file("COMMIT.md")
    personal_html = read_file("PERSONALSTATE.md", max_lines=40)

    section = lambda title, color, content: f"""
    <div style="background:#1a1a1f;border-radius:10px;padding:20px;margin-bottom:20px;border-left:4px solid {color};">
        <h2 style="margin:0 0 14px;font-size:16px;color:{color};text-transform:uppercase;letter-spacing:1px;">{title}</h2>
        <div style="color:#ccc;font-size:14px;line-height:1.6;">{content}</div>
    </div>
    """

    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#0d0d0f;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
<div style="max-width:640px;margin:0 auto;padding:32px 16px;">

  <!-- Header -->
  <div style="text-align:center;margin-bottom:32px;">
    <div style="font-size:32px;">🦾</div>
    <h1 style="color:#fff;font-size:24px;margin:8px 0 4px;">Dex Digest</h1>
    <p style="color:#555;font-size:13px;margin:0;">Week {week_num} · {date_str}</p>
  </div>

  {section("💡 Floats — Ideas in Motion", "#5b9cf6", float_html)}
  {section("🔥 Sparks — Build Queue", "#e07b54", spark_html)}
  {section("✅ Commitments — Open Items", "#4caf50", commit_html)}
  {section("🏠 Personal Pulse", "#a78bfa", personal_html)}

  <!-- Footer -->
  <div style="text-align:center;margin-top:32px;padding-top:20px;border-top:1px solid #1e1e2a;">
    <p style="color:#333;font-size:12px;margin:0;">Sent by Dex · askdex.rex@gmail.com</p>
    <p style="color:#222;font-size:11px;margin:4px 0 0;">Your AI partner, working while you sleep 🌙</p>
  </div>

</div>
</body>
</html>"""
    return html

# ── Send ──────────────────────────────────────────────────────────────────────
def send_digest(force=False):
    today = datetime.today().weekday()
    if today != 6 and not force:
        print("Not Sunday — skipping. Run with --force to override.")
        sys.exit(0)

    print("Building Dex Digest...")
    html_body = build_html()

    msg = MIMEMultipart("alternative")
    msg["From"]    = f"Dex 🦾 <{SENDER_EMAIL}>"
    msg["To"]      = RECIPIENT_EMAIL
    msg["Subject"] = f"🦾 Dex Digest — Week of {datetime.now().strftime('%B %d, %Y')}"

    msg.attach(MIMEText(html_body, "html"))

    context = ssl.create_default_context()
    print(f"Sending to {RECIPIENT_EMAIL}...")
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())

    print("✅ Dex Digest sent successfully.")

if __name__ == "__main__":
    force = "--force" in sys.argv
    send_digest(force=force)
