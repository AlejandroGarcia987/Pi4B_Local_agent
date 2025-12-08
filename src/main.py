import sys 
import platform
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from src.config import settings


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

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    logger.info("Agent is starting to poll for updates...")

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()