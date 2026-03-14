Dex Digest is a simple Python script that reads weekly summaries from COMMIT.md and SPARK.md files, formats a concise digest email, and sends it via Gmail SMTP. This provides a clear snapshot of open commitments, recent sparks, and upcoming priorities every Sunday to reduce mental overhead.

To use it:
1. Place your COMMIT.md and SPARK.md files in the same folder as dex_digest.py.
2. Edit dex_digest.py to set your Gmail address and an app password (generate one in your Google account security settings).
3. Run the script with: python dex_digest.py
4. To automate weekly sending, schedule this script with your OS scheduler (e.g., cron on Linux/macOS or Task Scheduler on Windows) to run every Sunday.

Make sure Python 3 is installed. No extra packages are required beyond the standard library and 'markdown' which you can install via: pip install markdown