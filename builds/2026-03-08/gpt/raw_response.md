=== FILENAME: dex_digest.py ===
#!/usr/bin/env python3
"""
Dex Digest Generator

Generates a weekly "Dex Digest" email draft summarizing:
- Open commitments from COMMIT.md
- Recent sparks from SPARK.md (entries in last 7 days)
- Upcoming priorities from PRIORITIES.md (tasks with due dates)

Outputs a plain-text email draft to DEX_DIGEST.txt

Usage:
    python dex_digest.py

"""

import os
import re
from datetime import datetime, timedelta

COMMIT_FILE = "COMMIT.md"
SPARK_FILE = "SPARK.md"
PRIORITIES_FILE = "PRIORITIES.md"
OUTPUT_FILE = "DEX_DIGEST.txt"

DATE_FORMATS = [
    "%Y-%m-%d",
    "%d-%m-%Y",
    "%m/%d/%Y",
    "%Y/%m/%d",
]

def parse_commitments():
    """
    Parse COMMIT.md for open commitments.
    Assumes commitments are markdown list items.
    Lines starting with '- [ ]' are open commitments.
    """
    if not os.path.isfile(COMMIT_FILE):
        return ["(No COMMIT.md file found)"]

    commitments = []
    with open(COMMIT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Open commitment: unchecked task
            if line.startswith("- [ ]"):
                # Remove markdown checkbox
                item = line[5:].strip()
                commitments.append(item)
            # Also accept simple list items if no checkboxes found
            elif line.startswith("- ") and "[ ]" not in line and "[x]" not in line:
                commitments.append(line[2:].strip())
    if not commitments:
        commitments.append("(No open commitments found)")
    return commitments

def parse_sparks():
    """
    Parse SPARK.md for recent sparks in last 7 days.
    Assumes sparks are markdown entries starting with a date header or date prefix.
    We'll look for lines starting with a date in ISO format or markdown date header (e.g. ## 2024-06-01)
    and collect sparks under that date.
    If no dates found, fallback to last 7 days of entries assuming each line is a spark with date prefix.

    Format assumed:
    ## 2024-06-01
    - Spark 1
    - Spark 2

    or

    2024-06-01: Spark text
    """
    if not os.path.isfile(SPARK_FILE):
        return ["(No SPARK.md file found)"]

    sparks = []
    current_date = None
    date_sparks = {}
    date_header_re = re.compile(r"^##\s*(\d{4}-\d{2}-\d{2})")
    date_prefix_re = re.compile(r"^(\d{4}-\d{2}-\d{2}):\s*(.*)")

    with open(SPARK_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            m_header = date_header_re.match(line)
            if m_header:
                current_date = m_header.group(1)
                if current_date not in date_sparks:
                    date_sparks[current_date] = []
                continue
            m_prefix = date_prefix_re.match(line)
            if m_prefix:
                d = m_prefix.group(1)
                text = m_prefix.group(2)
                if d not in date_sparks:
                    date_sparks[d] = []
                date_sparks[d].append(text)
                continue
            # If line starts with '-', treat as spark under current_date
            if line.startswith("- ") and current_date:
                date_sparks[current_date].append(line[2:].strip())

    # Filter sparks from last 7 days
    recent_sparks = []
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)

    for dstr, entries in date_sparks.items():
        try:
            d = datetime.strptime(dstr, "%Y-%m-%d").date()
        except ValueError:
            continue
        if week_ago <= d <= today:
            for e in entries:
                recent_sparks.append(f"{dstr}: {e}")

    if not recent_sparks:
        recent_sparks.append("(No recent sparks in last 7 days)")

    return recent_sparks

def parse_priorities():
    """
    Parse PRIORITIES.md for upcoming priorities.
    Assumes markdown list items with due dates in format:
    - Task description (due YYYY-MM-DD)
    or
    - Task description [due: YYYY-MM-DD]

    Returns tasks due in next 7 days sorted by due date.
    """
    if not os.path.isfile(PRIORITIES_FILE):
        return ["(No PRIORITIES.md file found)"]

    tasks = []
    due_re1 = re.compile(r"\(due (\d{4}-\d{2}-\d{2})\)")
    due_re2 = re.compile(r"\[due:\s*(\d{4}-\d{2}-\d{2})\]", re.IGNORECASE)

    today = datetime.now().date()
    week_later = today + timedelta(days=7)

    with open(PRIORITIES_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line.startswith("- "):
                continue
            task_text = line[2:].strip()
            due_date = None
            m1 = due_re1.search(task_text)
            m2 = due_re2.search(task_text)
            if m1:
                due_date_str = m1.group(1)
            elif m2:
                due_date_str = m2.group(1)
            else:
                due_date_str = None

            if due_date_str:
                try:
                    due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
                except ValueError:
                    due_date = None

            if due_date and today <= due_date <= week_later:
                tasks.append((due_date, task_text))

    tasks.sort(key=lambda x: x[0])

    if not tasks:
        return ["(No upcoming priorities in next 7 days)"]

    return [f"{t[0].isoformat()}: {t[1]}" for t in tasks]

def compose_email(commitments, sparks, priorities):
    """
    Compose the plain-text email draft.
    """
    lines = []
    lines.append("Subject: Dex Digest - Weekly Summary\n")
    lines.append("Hi Codi,\n")
    lines.append("Here's your weekly Dex Digest to keep you focused and reduce mental load.\n")

    lines.append("=== Open Commitments ===")
    for c in commitments:
        lines.append(f"- {c}")
    lines.append("")

    lines.append("=== Recent Sparks (last 7 days) ===")
    for s in sparks:
        lines.append(f"- {s}")
    lines.append("")

    lines.append("=== Upcoming Priorities (next 7 days) ===")
    for p in priorities:
        lines.append(f"- {p}")
    lines.append("")

    lines.append("Keep up the great work!\n")
    lines.append("Best,\nDex Bot\n")

    return "\n".join(lines)

def main():
    commitments = parse_commitments()
    sparks = parse_sparks()
    priorities = parse_priorities()

    email_text = compose_email(commitments, sparks, priorities)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(email_text)

    print(f"Dex Digest email draft generated and saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

=== END ===
=== FILENAME: README.md ===
Dex Digest Generator

This Python script generates a weekly "Dex Digest" email draft summarizing your open commitments, recent sparks from the past week, and upcoming priorities for the next 7 days. It reads from three markdown files in the current directory: COMMIT.md, SPARK.md, and PRIORITIES.md, then outputs a plain-text email draft to DEX_DIGEST.txt.

To use it, place your markdown files in the same folder as the script, then run:

    python dex_digest.py

The generated draft will be saved as DEX_DIGEST.txt, ready for review or sending.

=== END ===