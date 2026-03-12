This Python script automatically generates and sends a weekly "Dex Digest" email every Sunday evening. It reads from three markdown files—SPARK.md, FLOAT.md, and COMMIT.md—summarizes their contents, and emails the summary to a specified recipient using SMTP (Gmail). To run it, configure your Gmail SMTP credentials and recipient email in the script, then schedule it to run weekly on Sunday evenings (e.g., via cron). The script handles markdown parsing and email formatting for a clean digest.

Usage:
1. Update the SMTP and email settings in the script.
2. Place SPARK.md, FLOAT.md, and COMMIT.md in the same directory.
3. Run `python dex_digest.py` manually or schedule it weekly.