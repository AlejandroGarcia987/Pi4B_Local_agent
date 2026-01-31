from typing import Literal

Intent = Literal[
    "CALENDAR_TODAY",
    "CALENDAR_CREATE",
    "LLM_FALLBACK",
]


def detect_intent(text: str) -> Intent:
    t = text.lower().strip()

    # Calendar: today (más específico)
    calendar_today_keywords = [
        "hoy",
        "agenda",
        "tengo",
        "eventos hoy",
        "calendario hoy",
    ]

    if any(k in t for k in calendar_today_keywords):
        return "CALENDAR_TODAY"

    # Calendar: create (requiere verbo de acción)
    create_keywords = [
        "crear",
        "crea",
        "añadir",
        "añade",
        "programar",
        "programa",
    ]

    if any(k in t for k in create_keywords):
        return "CALENDAR_CREATE"

    return "LLM_FALLBACK"
