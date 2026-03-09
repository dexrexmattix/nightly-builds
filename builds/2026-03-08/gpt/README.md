Dex Digest Generator

This Python script generates a weekly "Dex Digest" email draft summarizing your open commitments, recent sparks from the past week, and upcoming priorities for the next 7 days. It reads from three markdown files in the current directory: COMMIT.md, SPARK.md, and PRIORITIES.md, then outputs a plain-text email draft to DEX_DIGEST.txt.

To use it, place your markdown files in the same folder as the script, then run:

    python dex_digest.py

The generated draft will be saved as DEX_DIGEST.txt, ready for review or sending.