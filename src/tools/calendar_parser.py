import logging
import json
from typing import Optional, Dict

from src.llm_client import ask_llm
from src.config import settings

CALENDAR_CREATE_PROMPT = """
You are an assistant that extracts structured calendar information.

Return ONLY valid JSON in this format:
{{
  "intent": "CALENDAR_CREATE",
  "title": "<event title or null>",
  "date_ref": "<today | tomorrow | day_after_tomorrow | null>",
  "weekday": "<monday | tuesday | wednesday | thursday | friday | saturday | sunday | null>",
  "time": "<HH:MM or null>"
}}

Rules:
- Do NOT return absolute dates (YYYY-MM-DD).
- If the user says "mañana", use "tomorrow".
- If the user mentions a weekday, use "weekday".
- Use null if information is missing.

User text:
{user_text}
"""



async def parse_calendar_create(text: str) -> Optional[Dict]:
    """
    Uses the LLM to extract structured calendar intent data.
    Returns a dict or None if parsing fails.
    """

    prompt = CALENDAR_CREATE_PROMPT.format(user_text=text)

    response = await ask_llm(
        prompt,
        timeout_s=settings.LLM_TIMEOUT_S,
    )

    logging.getLogger(__name__).info(f"LLM raw output: {response}")

    if not response:
        return None

    response = response.strip()

    # Remove markdown fences if present
    if response.startswith("```"):
        response = (
            response.replace("```json", "")
            .replace("```", "")
            .strip()
        )

    try:
        data = json.loads(response)
    except json.JSONDecodeError:
        return None

    # Hard validation
    if data.get("intent") != "CALENDAR_CREATE":
        return None

    # Normalize missing keys
    data.setdefault("title", None)
    data.setdefault("date_ref", None)
    data.setdefault("weekday", None)
    data.setdefault("time", None)

    return data
