---
BUILD TARGET: A quick Dex command to generate a weekly "Dex Digest" email summarizing open commitments, recent sparks, and upcoming priorities.  
WHY: Codi needs a low-noise, single-message weekly summary to reduce mental load and keep focus on meaningful tasks without distraction.  
WHAT TO BUILD: A simple Python script that pulls from COMMIT.md, SPARK.md (recent entries), and calendar or task files to compose a concise plain-text email draft for Sunday delivery. Include an easy command to trigger the draft generation.  
STACK: Python (with markdown parsing), email client integration optional but draft output as .txt is enough initially.  
ESTIMATED TIME: 1hr  
---
