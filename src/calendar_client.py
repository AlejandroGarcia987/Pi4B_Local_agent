from datetime import datetime, timedelta
import os
from typing import List, Dict

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

#CONFIG 
SCOPES = ["https://www.googleapis.com/auth/calendar"]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRETS_DIR = os.path.join(BASE_DIR, "secrets")

TOKEN_FILE = os.path.join(SECRETS_DIR, "google_calendar_token.json")


class GoogleCalendarClient:
    def __init__(self):
        self.service = self._authenticate()

    def _authenticate(self):
        if not os.path.exists(TOKEN_FILE):
            raise RuntimeError(
                "Google Calendar token not found. Run OAuth flow first."
            )

        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

        if not creds.valid:
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                raise RuntimeError("Invalid Google Calendar credentials")

        return build("calendar", "v3", credentials=creds)

    #READ

    def get_events_today(self) -> List[Dict]:
        now = datetime.utcnow()
        start = datetime.combine(now.date(), datetime.min.time()).isoformat() + "Z"
        end = datetime.combine(now.date(), datetime.max.time()).isoformat() + "Z"
        return self._get_events(start, end)

    def _get_events(self, time_min: str, time_max: str) -> List[Dict]:
        events_result = (
            self.service.events()
            .list(
                calendarId="primary",
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        return events_result.get("items", [])

    #WRITE

    def create_event(self, title: str, date: str, time: str):
        start_dt = datetime.fromisoformat(f"{date}T{time}")
        end_dt = start_dt + timedelta(hours=1)

        event = {
            "summary": title,
            "start": {
                "dateTime": start_dt.isoformat(),
                "timeZone": "Europe/Madrid",
            },
            "end": {
                "dateTime": end_dt.isoformat(),
                "timeZone": "Europe/Madrid",
            },
        }

        created_event = (
            self.service.events()
            .insert(calendarId="primary", body=event)
            .execute()
        )

        return created_event
