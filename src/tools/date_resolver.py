from datetime import date, timedelta

WEEKDAY_MAP = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

def resolve_event_date(data: dict) -> str | None:
    today = date.today()

    # Absolute date
    if data.get("date"):
        return data["date"]

    # Relative references
    ref = data.get("date_ref")
    if ref == "today":
        return today.isoformat()
    if ref == "tomorrow":
        return (today + timedelta(days=1)).isoformat()
    if ref == "day_after_tomorrow":
        return (today + timedelta(days=2)).isoformat()

    # Weekday
    weekday = data.get("weekday")
    if weekday in WEEKDAY_MAP:
        target = WEEKDAY_MAP[weekday]
        days_ahead = (target - today.weekday()) % 7
        days_ahead = 7 if days_ahead == 0 else days_ahead
        return (today + timedelta(days=days_ahead)).isoformat()

    return None
