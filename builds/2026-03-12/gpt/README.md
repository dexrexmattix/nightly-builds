Dex Digest is a simple Python script that compiles a weekly summary email from three markdown files: COMMIT.md (open commitments), SPARK.md (key sparks), and TASKS.md (task list with due dates). It sends this digest every Sunday morning via your Gmail account to help you stay focused on what matters each week.

To use it:
1. Prepare COMMIT.md, SPARK.md, and TASKS.md in the same folder as the script.
2. Format TASKS.md tasks like this:
   - [ ] Task description (due YYYY-MM-DD)
   - [x] Completed task (due YYYY-MM-DD)
3. Set environment variables in your terminal:
   - DEX_GMAIL_USER = your Gmail address
   - DEX_GMAIL_APP_PASSWORD = your Gmail app password (create one in Google account security settings)
   - (Optional) DEX_TO_EMAIL = recipient email address (defaults to your Gmail user)
4. Run the script with Python 3:
   python dex_digest.py

You can schedule this script to run automatically every Sunday morning using your OS scheduler (cron on Linux/macOS or Task Scheduler on Windows).