Dex Digest is a simple Python script that compiles a weekly summary email every Sunday morning. It reads your open commitments from COMMIT.md, sparks from SPARK.md, and upcoming events from a local calendar export file named calendar.ics. It then sends a clean summary email via SMTP to your email address, helping you keep track of priorities without daily noise.

To use it:
1. Place your COMMIT.md, SPARK.md, and calendar.ics files in the same folder as dex_digest.py.
2. Set the following environment variables with your SMTP and email info:
   - SMTP_SERVER (e.g., smtp.gmail.com)
   - SMTP_PORT (usually 587)
   - SMTP_USER (your SMTP username/email)
   - SMTP_PASSWORD (your SMTP password or app password)
   - FROM_EMAIL (the sender email address)
   - TO_EMAIL (the recipient email address)
3. Run the script from the terminal:
   ```
   python dex_digest.py
   ```
You can schedule this script to run every Sunday morning using your OS scheduler (cron, Task Scheduler, etc.) for automatic weekly emails.