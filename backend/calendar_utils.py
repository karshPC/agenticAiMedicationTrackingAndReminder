from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime

import os
from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/calendar']

credentials = service_account.Credentials.from_service_account_file(
    'calendar_credentials.json',
    scopes=SCOPES
)

service = build('calendar', 'v3', credentials=credentials)
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")

print("📅 USING CALENDAR:", CALENDAR_ID)

def create_event(summary, description, time_str):

    now = datetime.now()

    event_time = datetime.strptime(time_str, "%H:%M")
    event_time = event_time.replace(
        year=now.year,
        month=now.month,
        day=now.day
    )

    start = event_time.isoformat()
    end = event_time.isoformat()

    event = {
        'summary': summary,
        'description': description,
        'start': {'dateTime': start, 'timeZone': 'Asia/Kolkata'},
        'end': {'dateTime': end, 'timeZone': 'Asia/Kolkata'},
        'recurrence': ['RRULE:FREQ=DAILY']
    }

    created_event = service.events().insert(
        calendarId=CALENDAR_ID,
        body=event
    ).execute()

    print("📅 Event created:", summary)

    # ✅ RETURN EVENT ID
    return created_event["id"]

def delete_event(event_id):
    try:
        service.events().delete(
            calendarId=CALENDAR_ID,
            eventId=event_id
        ).execute()

        print("🗑️ Event deleted:", event_id)

    except Exception as e:
        print("❌ Delete error:", e)