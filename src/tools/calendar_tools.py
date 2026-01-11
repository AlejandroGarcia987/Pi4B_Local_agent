from src.calendar_client import GoogleCalendarClient

def get_today_events():
    client = GoogleCalendarClient()
    return client.get_events_today()

def get_next_days_events(days: int = 7):
    client = GoogleCalendarClient()
    return client.get_events_next_days(days)
