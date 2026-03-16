This Python script compiles a weekly "Dex Digest" email by reading open commitments from COMMIT.md, recent floats from FLOAT.md, and sparks from SPARK.md. It formats these into a clean email template and sends the email via SMTP (Gmail recommended) every Sunday night. To run, configure your SMTP email credentials in config.json, ensure the three markdown files are in the same folder, and run the script manually or schedule it weekly with a cron job or Windows Task Scheduler.

Usage:
1. Fill in your email and SMTP details in config.json.
2. Place COMMIT.md, FLOAT.md, and SPARK.md in the same folder.
3. Run `python dex_digest.py` to send the email immediately.
4. Automate weekly runs via your OS scheduler for Sunday night delivery.