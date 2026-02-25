"""Typenschild-Scanner Telegram Bot – Hauptmodul."""
import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)

import config
from db.database import init_db
from bot.handlers.start import get_start_handler
from bot.handlers.standort import (
    standort_command,
    wechsel_command,
    status_command,
    hilfe_command,
    get_standort_callback_handler,
)
from bot.handlers.scan import foto_scan, sprach_notiz, text_notiz, get_bestaetigung_callback_handler, get_laufzeit_callback_handler
from bot.handlers.liste import liste_command, suche_command
from bot.handlers.bericht import bericht_command
from bot.handlers.export import export_command

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main():
    """Bot starten."""
    logger.info("Initialisiere Datenbank...")
    init_db()

    logger.info("Starte Typenschild-Scanner Bot...")
    app = ApplicationBuilder().token(config.TELEGRAM_BOT_TOKEN).build()

    # Handler registrieren (Reihenfolge wichtig!)
    # 1. Conversation Handler für /start (hat Priorität)
    app.add_handler(get_start_handler())

    # 2. Befehle
    app.add_handler(CommandHandler("standort", standort_command))
    app.add_handler(CommandHandler("wechsel", wechsel_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("liste", liste_command))
    app.add_handler(CommandHandler("suche", suche_command))
    app.add_handler(CommandHandler("bericht", bericht_command))
    app.add_handler(CommandHandler("export", export_command))
    app.add_handler(CommandHandler("hilfe", hilfe_command))

    # 3. Callback für Inline-Buttons
    app.add_handler(get_standort_callback_handler())
    app.add_handler(get_bestaetigung_callback_handler())
    app.add_handler(get_laufzeit_callback_handler())

    # 4. Nachrichten-Handler (Fotos = Typenschild-Scan, Text/Sprache = Notizen)
    app.add_handler(MessageHandler(filters.PHOTO, foto_scan))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_notiz))
    app.add_handler(MessageHandler(filters.VOICE, sprach_notiz))

    logger.info("Bot läuft! Drücke Ctrl+C zum Beenden.")
    app.run_polling()


if __name__ == "__main__":
    main()
