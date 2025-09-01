import requests

def extract_schedule_from_email(email_text):
    prompt = f"""
You are a helpful AI assistant that extracts meeting and scheduling information from email content.

Email:
\"\"\"{email_text}\"\"\"

If the email contains an event, extract:
- Title
- Date (in YYYY-MM-DD format, e.g., 2025-01-15)
- Start Time (in HH:MM format, e.g., 14:30 or 2:30PM)
- End Time (in HH:MM format, e.g., 15:30 or 3:30PM)
- Location (if any)
- Participants (if mentioned)

IMPORTANT: 
- Use YYYY-MM-DD format for dates (e.g., 2025-01-15, not 01/15/2025)
- Use 24-hour format for times when possible (e.g., 14:30 instead of 2:30PM)
- If only 12-hour format is available, use it (e.g., 2:30PM)

Respond ONLY in this JSON format:
{{
  "title": "...",
  "date": "YYYY-MM-DD",
  "start_time": "HH:MM or H:MMAM/PM",
  "end_time": "HH:MM or H:MMAM/PM",
  "location": "...",
  "participants": [...]
}}

If there's no event, respond:
{{ "action": "No scheduling info found." }}
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",  # You can switch to llama3, phi3, etc.
            "prompt": prompt,
            "stream": False
        }
    )
    
    print("🔍 Raw LLM Response:", response.json())
    return response.json()["response"]
   