import datetime
import os
from typing import List, Dict

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


# ===== CONFIG =====
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRETS_DIR = os.path.join(BASE_DIR, "secrets")

TOKEN_FILE = os.path.join(SECRETS_DIR, "google_calendar_token.json")


class GoogleCalendarClient:
    def __init__(self):
        self.service = self._authenticate()

    def _authenticate(self):
        if not os.path.exists(TOKEN_FILE):
            raise RuntimeError(
                "Google Calendar token not found. "
                "Run OAuth flow on host first."
            )

        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

        if not creds.valid:
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                raise RuntimeError("Invalid Google Calendar credentials")

        return build("calendar", "v3", credentials=creds)

    def get_events_today(self) -> List[Dict]:
        now = datetime.datetime.utcnow()
        start = datetime.datetime.combine(
            now.date(), datetime.time.min
        ).isoformat() + "Z"
        end = datetime.datetime.combine(
            now.date(), datetime.time.max
        ).isoformat() + "Z"

        return self._get_events(start, end)

    def get_events_next_days(self, days: int = 7) -> List[Dict]:
        now = datetime.datetime.utcnow()
        end = now + datetime.timedelta(days=days)

        return self._get_events(
            now.isoformat() + "Z",
            end.isoformat() + "Z",
        )

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
