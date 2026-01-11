import sys 
import platform
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from src.config import settings
from src.llm_client import ask_llm
from src.tools.calendar_tools import get_today_events

# Logging basic config

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



async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Forward User message to LLM and answer (simple)
    user_text = update.message.text
    sent = await update.message.reply_text(f"Received message: '{user_text}'. Processing...")

    # Build a short prompt; tune prompt engineering here
    prompt = f"User: {user_text}\n\nAnswer in Spanish"

    # Call LLM (async)
    llm_resp = await ask_llm(prompt, timeout_s=settings.LLM_TIMEOUT_S)

    if llm_resp:
        # send final answer (edit the placeholder message)
        try:
            await context.bot.edit_message_text(chat_id=sent.chat_id, message_id=sent.message_id, text=llm_resp)
        except Exception:
            # fallback: send a new message
            await context.bot.send_message(chat_id=sent.chat_id, text=llm_resp)
    else:
        try:
            await context.bot.edit_message_text(chat_id=sent.chat_id, message_id=sent.message_id,
                                                text="No response from LLM (timeout/error).")
        except Exception:
            await context.bot.send_message(chat_id=sent.chat_id, text="No response from LLM (timeout/error).")


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
