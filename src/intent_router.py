from typing import Literal

Intent = Literal[
    "CALENDAR_TODAY",
    "CALENDAR_UNKNOWN",
    "LLM_FALLBACK",
]

def detect_intent(text: str) -> Intent:
    t = text.lower().strip()

    # Calendar: today
    calendar_today_keywords = [
        "hoy",
        "agenda",
        "tengo",
        "eventos",
        "calendario",
    ]

    if any(k in t for k in calendar_today_keywords):
        return "CALENDAR_TODAY"

    return "LLM_FALLBACK"
