from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import datetime
import os
import json
from datetime import datetime as dt


# SCOPES for creating and viewing calendar events
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def get_calendar_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('calendar', 'v3', credentials=creds)
    return service

def validate_and_format_datetime(date_str, time_str):
    """Validate and format date and time strings for Google Calendar API"""
    try:
        # Handle various date formats
        date_formats = [
            '%Y-%m-%d',      # 2025-01-15
            '%m/%d/%Y',      # 01/15/2025
            '%d/%m/%Y',      # 15/01/2025
            '%B %d, %Y',     # January 15, 2025
            '%b %d, %Y',     # Jan 15, 2025
        ]
        
        parsed_date = None
        for fmt in date_formats:
            try:
                parsed_date = dt.strptime(date_str, fmt)
                break
            except ValueError:
                continue
        
        if not parsed_date:
            raise ValueError(f"Could not parse date: {date_str}")
        
        # Handle various time formats
        time_formats = [
            '%H:%M:%S',      # 15:00:00
            '%H:%M',         # 15:00
            '%I:%M%p',       # 3:00PM
            '%I:%M %p',      # 3:00 PM
        ]
        
        parsed_time = None
        for fmt in time_formats:
            try:
                parsed_time = dt.strptime(time_str, fmt)
                break
            except ValueError:
                continue
        
        if not parsed_time:
            raise ValueError(f"Could not parse time: {time_str}")
        
        # Combine date and time
        combined_datetime = dt.combine(parsed_date.date(), parsed_time.time())
        
        # Format for Google Calendar API (ISO 8601)
        return combined_datetime.strftime('%Y-%m-%dT%H:%M:%S')
        
    except Exception as e:
        raise ValueError(f"Error formatting datetime: {e}")

def create_event(event_data):
    service = get_calendar_service()

    try:
        # Validate required fields
        required_fields = ['title', 'date', 'start_time', 'end_time']
        for field in required_fields:
            if field not in event_data:
                raise ValueError(f"Missing required field: {field}")
        
        print(f"📅 Creating event with data: {json.dumps(event_data, indent=2)}")
        
        # Format start and end times
        start_datetime = validate_and_format_datetime(event_data['date'], event_data['start_time'])
        end_datetime = validate_and_format_datetime(event_data['date'], event_data['end_time'])
        
        print(f"🕐 Formatted start time: {start_datetime}")
        print(f"🕐 Formatted end time: {end_datetime}")

        event = {
            'summary': event_data['title'],
            'location': event_data.get('location', ''),
            'description': 'Created by AI Email Scheduler Agent',
            'start': {
                'dateTime': start_datetime,
                'timeZone': 'America/New_York',  # Change if needed
            },
            'end': {
                'dateTime': end_datetime,
                'timeZone': 'America/New_York',
            },
        }
        
        # Add attendees if provided
        if event_data.get('participants'):
            event['attendees'] = [{'email': p} for p in event_data.get('participants', [])]

        print(f"📤 Sending event to Google Calendar API...")
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        
        print(f"✅ Event created successfully!")
        print(f"🔗 Event link: {created_event.get('htmlLink')}")
        print(f"📅 Event ID: {created_event.get('id')}")
        
        return created_event
        
    except Exception as e:
        print(f"❌ Failed to create event: {e}")
        print(f"🔍 Event data that failed: {json.dumps(event_data, indent=2)}")
        raise
