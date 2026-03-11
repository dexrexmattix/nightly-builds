# Dex Digest Weekly Email Summary

This Python script generates and emails a weekly "Dex Digest" summary every Sunday morning. It consolidates key items from four markdown files (`COMMIT.md`, `FLOAT.md`, `SPARK.md`, and `CALENDAR.md`) into a clear, actionable overview to help reduce cognitive load and keep you aligned for the week ahead.

## How to Use

1. Place your task and idea files (`COMMIT.md`, `FLOAT.md`, `SPARK.md`) and your calendar events file (`CALENDAR.md`) in the same folder as the script.  
   - `COMMIT.md`, `FLOAT.md`, and `SPARK.md` should contain simple markdown lists or lines describing your items.  
   - `CALENDAR.md` should list events in the format: `YYYY-MM-DD - Event description`.

2. Edit the `dex_digest.py` file to configure your email settings:  
   - `SMTP_SERVER`, `SMTP_PORT` (default is Gmail SMTP)  
   - `SMTP_USERNAME` and `SMTP_PASSWORD` (use an app password if using Gmail)  
   - `EMAIL_FROM` and `EMAIL_TO` addresses.

3. Run the script on a Sunday morning (or schedule it via cron or task scheduler):  
   ```bash
   python dex_digest.py
   ```

4. The script will send an email with a markdown-formatted summary of your open commitments, floats, sparks, and calendar events for the upcoming week.

---

This tool helps you stay organized and focused by consolidating scattered tasks and ideas into one concise weekly email.