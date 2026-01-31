import sys
import platform
import logging
from datetime import date, timedelta

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from src.config import settings
from src.llm_client import ask_llm
from src.intent_router import detect_intent
from src.tools.calendar_tools import get_today_events
from src.tools.calendar_parser import parse_calendar_create
from src.calendar_client import GoogleCalendarClient

# In-memory state (chat_id -> pending event)
PENDING_CALENDAR_EVENTS = {}

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# Commands

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        f"Hello {user.mention_html()}! I am your Local Agent."
    )


async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        events = get_today_events()

        if not events:
            await update.message.reply_text("No events scheduled for today.")
            return

        lines = ["*Today's events:*"]
        for e in events:
            start = e["start"].get("dateTime", e["start"].get("date"))
            summary = e.get("summary", "No title")
            lines.append(f"- {start} · {summary}")

        await update.message.reply_text(
            "\n".join(lines),
            parse_mode="Markdown",
        )

    except Exception:
        logger.exception("Calendar error")
        await update.message.reply_text("Error reading calendar.")


# Calendar creation flow

async def handle_calendar_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text

    await update.message.reply_text("Entendido. Analizando el evento...")

    data = await parse_calendar_create(user_text)
    logger.info(f"Parsed calendar data: {data}")

    if not data:
        await update.message.reply_text(
            "No he podido entender el evento. ¿Puedes reformularlo?"
        )
        return

    chat_id = update.effective_chat.id
    PENDING_CALENDAR_EVENTS[chat_id] = {
        "raw_text": user_text,
        "data": data,
    }

    lines = ["*Nuevo evento detectado:*"]

    if data.get("title"):
        lines.append(f"- Título: {data['title']}")
    if data.get("date"):
        lines.append(f"- Fecha: {data['date']}")
    if data.get("time"):
        lines.append(f"- Hora: {data['time']}")

    lines.append("")
    lines.append("¿Quieres que lo cree en el calendario? (sí / no)")

    await update.message.reply_text(
        "\n".join(lines),
        parse_mode="Markdown",
    )


async def handle_calendar_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Handles yes/no confirmation.
    Returns True if handled.
    """
    chat_id = update.effective_chat.id
    text = update.message.text.lower().strip()

    if chat_id not in PENDING_CALENDAR_EVENTS:
        return False

    if text not in {"sí", "si", "no"}:
        return False

    pending = PENDING_CALENDAR_EVENTS.pop(chat_id)
    data = pending["data"]
    raw_text = pending["raw_text"]

    if text == "no":
        await update.message.reply_text("Evento cancelado.")
        return True

    # Resolve date if missing
    event_date = data.get("date")
    if not event_date:
        raw_lower = raw_text.lower()

        if "mañana" in raw_lower:
            event_date = (date.today() + timedelta(days=1)).isoformat()
        elif "pasado mañana" in raw_lower:
            event_date = (date.today() + timedelta(days=2)).isoformat()
        else:
            await update.message.reply_text(
                "No he podido determinar la fecha del evento."
            )
            return True

    try:
        calendar = GoogleCalendarClient()
        calendar.create_event(
            title=data.get("title") or "Evento",
            date=event_date,
            time=data.get("time"),
        )
    except Exception:
        logger.exception("Error creating calendar event")
        await update.message.reply_text(
            "Ha ocurrido un error al crear el evento."
        )
        return True

    await update.message.reply_text("Evento creado en el calendario.")
    return True


# LLM fallback

async def handle_llm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text

    sent = await update.message.reply_text(
        f"Received message: '{user_text}'. Processing..."
    )

    prompt = f"User: {user_text}\n\nAnswer in Spanish"
    llm_resp = await ask_llm(prompt, timeout_s=settings.LLM_TIMEOUT_S)

    if llm_resp:
        await context.bot.edit_message_text(
            chat_id=sent.chat_id,
            message_id=sent.message_id,
            text=llm_resp,
        )
    else:
        await update.message.reply_text(
            "No response from LLM (timeout/error)."
        )


# Main text router

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Confirmation step
    handled = await handle_calendar_confirmation(update, context)
    if handled:
        return

    text = update.message.text
    intent = detect_intent(text)

    if intent == "CALENDAR_TODAY":
        await today_command(update, context)
        return

    if intent == "CALENDAR_CREATE":
        await handle_calendar_create(update, context)
        return

    await handle_llm(update, context)


# App bootstrap

def main():
    print("--- Local Agent System Info ---")
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Python Version: {sys.version}")

    application = Application.builder().token(
        settings.TELEGRAM_BOT_TOKEN
    ).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("today", today_command))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, echo)
    )

    logger.info("Agent is starting to poll for updates...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
