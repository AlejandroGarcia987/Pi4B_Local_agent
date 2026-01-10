from src.calendar_client import GoogleCalendarClient

def main():
    client = GoogleCalendarClient()

    print("Events today:\n")
    events = client.get_events_today()

    if not events:
        print("No events today.")
        return

    for e in events:
        start = e["start"].get("dateTime", e["start"].get("date"))
        print(f"- {start} | {e.get('summary', 'No title')}")

if __name__ == "__main__":
    main()
