```markdown
=== README.md ===
This script generates a weekly "Dex Digest" email summarizing open commitments, recent sparks, and upcoming priorities. It pulls data from `COMMIT.md`, `SPARK.md`, and calendar or task files to compose a concise plain-text draft. To generate the digest, run `python dex_digest.py` in your terminal on Sunday.

=== END ===

=== dex_digest.py ===
```python
import os
from datetime import datetime, timedelta
import markdown2

def read_markdown_file(file_path):
    if not os.path.exists(file_path):
        return ""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def parse_commitments(commit_text):
    lines = commit_text.split('\n')
    commitments = [line for line in lines if line.startswith('-')]
    return "\n".join(commitments)

def parse_sparks(spark_text):
    lines = spark_text.split('\n')
    sparks = [line for line in lines if line.startswith('*')]
    return "\n".join(sparks)

def get_upcoming_priorities():
    now = datetime.now()
    upcoming_tasks = []
    # Simulating task fetching. Replace with actual calendar/task logic.
    tasks = [
        {"title": "Team Meeting", "date": now + timedelta(days=1)},
        {"title": "Project Review", "date": now + timedelta(days=3)}
    ]
    
    for task in tasks:
        if task["date"] > now and task["date"] < now + timedelta(weeks=1):
            upcoming_tasks.append(f"- {task['title']} on {task['date'].strftime('%Y-%m-%d')}")
    
    return "\n".join(upcoming_tasks)

def generate_digest():
    commit_text = read_markdown_file('COMMIT.md')
    spark_text = read_markdown_file('SPARK.md')

    commitments = parse_commitments(commit_text)
    sparks = parse_sparks(spark_text)
    priorities = get_upcoming_priorities()

    digest_content = f"""
Dex Digest - {datetime.now().strftime('%Y-%m-%d')}

Open Commitments:
{commitments if commitments else "No open commitments."}

Recent Sparks:
{sparks if sparks else "No recent sparks."}

Upcoming Priorities:
{priorities if priorities else "No upcoming priorities."}
"""

    with open('dex_digest.txt', 'w', encoding='utf-8') as file:
        file.write(digest_content)

if __name__ == "__main__":
    generate_digest()
```
=== END ===
```