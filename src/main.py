import sys 
import platform
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from src.config import settings
from src.llm_client import ask_llm
from src.tools.calendar_tools import get_today_events
from src.intent_router import detect_intent
from src.tools.calendar_parser import parse_calendar_create


# Basic Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Telegram Handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start."""
    user = update.effective_user
    await update.message.reply_html(
        f"Hello {user.mention_html()}! I am your Local Agent, ready for service.",
    )


async def handle_calendar_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text

    await update.message.reply_text("Entendido. Analizando el evento…")

    data = await parse_calendar_create(user_text)
    logger.info(f"Pared calendar data: {data}")

    if not data:
        await update.message.reply_text(
            "No he podido entender bien el evento. "
            "¿Puedes reformularlo?"
        )
        return

    lines = ["*Nuevo evento detectado:*"]

    if data.get("title"):
        lines.append(f"- Título: {data['title']}")
    if data.get("date"):
        lines.append(f"- Fecha: {data['date']}")
    if data.get("time"):
        lines.append(f"- Hora: {data['time']}")
    if data.get("duration_minutes"):
        lines.append(f"- Duración: {data['duration_minutes']} min")
    if data.get("description"):
        lines.append(f"- Descripción: {data['description']}")

    lines.append("")
    lines.append("¿Quieres que lo cree en el calendario? (sí / no)")

    # Save state for next 
    context.user_data["pending_calendar_event"] = data

    await update.message.reply_text(
        "\n".join(lines),
        parse_mode="Markdown"
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
            parse_mode="Markdown"
        )

    except Exception:
        logger.exception("Calendar error")
        await update.message.reply_text("Error reading calendar.")




async def handle_llm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text

    sent = await update.message.reply_text(
        f"Received message: '{user_text}'. Processing..."
    )

    prompt = f"User: {user_text}\n\nAnswer in Spanish"

    llm_resp = await ask_llm(prompt, timeout_s=settings.LLM_TIMEOUT_S)

    if llm_resp:
        try:
            await context.bot.edit_message_text(
                chat_id=sent.chat_id,
                message_id=sent.message_id,
                text=llm_resp,
            )
        except Exception:
            await context.bot.send_message(
                chat_id=sent.chat_id,
                text=llm_resp,
            )
    else:
        await context.bot.send_message(
            chat_id=sent.chat_id,
            text="No response from LLM (timeout/error).",
        )



async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    intent = detect_intent(text)

    if intent == "CALENDAR_TODAY":
        await today_command(update, context)
        return

    if intent == "CALENDAR_CREATE":
        await handle_calendar_create(update, context)
        return

    # fallback to LLM
    await handle_llm(update, context)







async def _echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.lower().strip()

    # hard rules first
    if text in {"hi", "hola", "hello"}:
        await update.message.reply_text("¡Hola! ¿En qué puedo ayudarte?")
        return

    if "calendar" in text or "agenda" in text:
        await update.message.reply_text(
            "Puedes usar /today para ver tus eventos de hoy."
        )
        return

    #fallback to LLM
    await handle_llm(update, context)


async def echo_legacy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echoes user message"""
    await update.message.reply_text(f"Received message: '{update.message.text}'. Processing...")

def main():

    # Init
    print("--- Local Agent System Info ---")
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Python Version: {sys.version}")

    # Load token
    token = settings.TELEGRAM_BOT_TOKEN

    # Init and bot config
    application = Application.builder().token(token).build()

    #Suscribe handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("today", today_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    logger.info("Agent is starting to poll for updates...")

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
