Dex Digest is a simple Python script that compiles key points from FLOAT.md, SPARK.md, and COMMIT.md files into a concise weekly email summary. It is designed to run on Sundays and sends the digest via Gmail SMTP to help Codi stay organized with a single overview message.

To use:
1. Place your FLOAT.md, SPARK.md, and COMMIT.md files in the same folder as dex_digest.py.
2. Edit dex_digest.py to set your Gmail address, recipient email, and app password (or email password if less secure apps are allowed).
3. Run the script on a Sunday using: python dex_digest.py
4. The script will send the weekly digest email automatically.

Note: For Gmail SMTP, you may need to create an App Password if you have 2FA enabled or allow less secure apps access.