---
BUILD TARGET: A simple Sunday "Dex Digest" email summarizing weekly open commitments, sparks, and upcoming events.  
WHY: Codi needs a low-noise, once-weekly briefing to reduce mental overhead and keep track of priorities without daily noise or digging through multiple sources.  
WHAT TO BUILD: A Python script that pulls from COMMIT.md, SPARK.md, and calendar events (Google Calendar API or local calendar export), compiles a clean summary email, and sends it via SMTP or Dex’s email account every Sunday morning.  
STACK: Python (requests, markdown parser, smtplib)  
ESTIMATED TIME: 1hr  
---
