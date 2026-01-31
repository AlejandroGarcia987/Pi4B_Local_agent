import json
from typing import Optional, Dict

from src.llm_client import ask_llm

CALENDAR_CREATE_PROMPT = """
You are an assistant that extracts structured calendar information.

Return ONLY valid JSON in this format:
{{
  "intent": "CALENDAR_CREATE",
  "title": "<event title or null>",
  "date": "<YYYY-MM-DD or null>",
  "time": "<HH:MM or null>"
}}

User text:
{user_text}
"""


async def parse_calendar_create(text: str) -> Optional[Dict]:
    """
    Uses the LLM to extract structured calendar event data from free text.
    Returns a dict if parsing succeeds, or None if it fails.
    """

    prompt = CALENDAR_CREATE_PROMPT.format(user_text=text)

    response = await ask_llm(prompt)

    if not response:
        return None

    try:
        data = json.loads(response)
    except json.JSONDecodeError:
        return None

    #Verify correct action
    if data.get("intent") != "CALENDAR_CREATE":
        return None

    return data

