from calendar_updater import create_event
from datetime import datetime, timedelta

# Get tomorrow's date
tomorrow = datetime.now() + timedelta(days=1)
tomorrow_str = tomorrow.strftime('%Y-%m-%d')

# Test dummy event (tomorrow + 1 hour)
event = {
    "title": "Test Calendar Event",
    "date": tomorrow_str,  # Tomorrow's date
    "start_time": "15:00:00",  # 3:00 PM
    "end_time": "16:00:00",    # 4:00 PM
    "location": "Virtual Meeting",
    "participants": ["sameerrithwik13@gmail.com"]  # use your own email if you want
}

create_event(event)
