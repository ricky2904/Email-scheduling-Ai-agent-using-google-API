import os
import base64
import re
import json
import time
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email import message_from_bytes
from google.auth.transport.requests import Request
from llm_agent import extract_schedule_from_email
from calendar_updater import create_event
from datetime import datetime


# SCOPES for Gmail and Calendar
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar.events'
]

def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


    
def get_unread_emails(service, max_results=5):
    results = service.users().messages().list(
        userId='me',
        labelIds=['CATEGORY_PERSONAL', 'UNREAD'],
        maxResults=max_results
    ).execute()

    messages = results.get('messages', [])
    if not messages:
        print("✅ No unread emails.")
        return []

    print(f"📨 Found {len(messages)} unread email(s):\n")

    for msg in messages:
        msg_data = service.users().messages().get(
            userId='me', id=msg['id'], format='full'
        ).execute()

        headers = msg_data['payload'].get('headers', [])
        subject = sender = ""
        for header in headers:
            if header['name'] == 'Subject':
                subject = header['value']
            if header['name'] == 'From':
                sender = header['value']
        snippet = msg_data.get('snippet', '')

        print(f"🔹 From: {sender}")
        print(f"🔹 Subject: {subject}")
        print(f"🔹 Snippet: {snippet}\n")

        structured = extract_schedule_from_email(snippet)
        print("🧠 Raw LLM Output:\n", structured)

        try:
            match = re.search(r'\{[\s\S]*\}', structured)
            if not match:
                raise ValueError("No JSON object found in LLM response.")

            json_str = match.group()
            data = json.loads(json_str)

            if "action" not in data:
                print("\n📋 Proposed Event:")
                print(f"Title       : {data['title']}")
                print(f"Date        : {data['date']}")
                print(f"Start Time  : {data['start_time']}")
                print(f"End Time    : {data['end_time']}")
                print(f"Location    : {data.get('location', 'N/A')}")
                print(f"Participants: {', '.join(data.get('participants', []))}")
                
                create_event(data)
                print("✅ Event created successfully.")
                print("--------------------------------")
                

        except Exception as e:
            print(f"⚠️ Couldn't parse or schedule event: {e}")
        
    

def run_agent():
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)

    while True:
        print("\n🔁 Checking for unread emails...\n")
        try:
            get_unread_emails(service)
        except Exception as e:
            print(f"❌ Error during agent run: {e}")
        print("⏳ Sleeping for 5 minutes...\n")
        time.sleep(5 * 60)
        
if __name__ == '__main__':
    run_agent()
