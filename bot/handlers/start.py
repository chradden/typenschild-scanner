"""Handler für /start – Registrierung neuer Benutzer mit Passwort-Schutz."""
from telegram import Update
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler,
    MessageHandler, filters,
)

import config
from db.database import get_session
from db.models import Benutzer

# Conversation States
WARTE_AUF_PASSWORT = 0
WARTE_AUF_NAME = 1


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prüft ob Benutzer existiert, sonst Registrierung starten."""
    telegram_id = update.effective_user.id
    name = None

    with get_session() as session:
        benutzer = session.query(Benutzer).filter_by(telegram_id=telegram_id).first()
        if benutzer:
            name = benutzer.name

    if name:
        await update.message.reply_text(
            f"Willkommen zurück, {name}! ⚡\n\n"
            f"Nutze /status um deinen aktiven Standort zu sehen.\n"
            f"Nutze /hilfe für alle Befehle."
        )
        return ConversationHandler.END

    # Passwort-Schutz aktiv?
    if config.BOT_PASSWORT:
        await update.message.reply_text(
            "🔒 Willkommen beim Typenschild-Scanner!\n\n"
            "Dieser Bot ist passwortgeschützt.\n"
            "Bitte gib das Zugangspasswort ein:"
        )
        return WARTE_AUF_PASSWORT
    else:
        await update.message.reply_text(
            "Willkommen beim Typenschild-Scanner! ⚡\n\n"
            "Ich helfe dir, Typenschilder von Verbrauchern zu scannen "
            "und die technischen Daten automatisch zu erfassen.\n\n"
            "Bitte gib deinen Namen ein:"
        )
        return WARTE_AUF_NAME


async def passwort_eingabe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prüft das eingegebene Passwort."""
    eingabe = update.message.text.strip()

    # Nachricht mit Passwort sofort löschen (Datenschutz)
    try:
        await update.message.delete()
    except Exception:
        pass

    if eingabe == config.BOT_PASSWORT:
        await update.effective_chat.send_message(
            "✅ Passwort korrekt!\n\n"
            "Willkommen beim Typenschild-Scanner! ⚡\n"
            "Ich helfe dir, Typenschilder von Verbrauchern zu scannen "
            "und die technischen Daten automatisch zu erfassen.\n\n"
            "Bitte gib deinen Namen ein:"
        )
        return WARTE_AUF_NAME
    else:
        versuche = context.user_data.get("passwort_versuche", 0) + 1
        context.user_data["passwort_versuche"] = versuche

        if versuche >= 3:
            await update.effective_chat.send_message(
                "❌ Zu viele Fehlversuche. Zugang gesperrt.\n"
                "Kontaktiere den Administrator."
            )
            return ConversationHandler.END

        await update.effective_chat.send_message(
            f"❌ Falsches Passwort. Versuch {versuche}/3.\n"
            "Bitte erneut eingeben:"
        )
        return WARTE_AUF_PASSWORT


async def name_eingabe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Speichert den Namen und schließt die Registrierung ab."""
    name = update.message.text.strip()
    telegram_id = update.effective_user.id

    with get_session() as session:
        benutzer = Benutzer(telegram_id=telegram_id, name=name)
        session.add(benutzer)

    context.user_data.pop("passwort_versuche", None)

    await update.message.reply_text(
        f"Hallo {name}! ✅\n\n"
        f"Dein Account wurde erstellt.\n"
        f"Lege jetzt deinen ersten Standort an mit:\n"
        f"/standort <Name>\n\n"
        f"Beispiel: /standort Bürogebäude Schönhauser Allee 45\n\n"
        f"🎯 **Tipp:** Teile deinen Standort (Büroklammer → Standort), "
        f"um die Adresse automatisch zu hinterlegen!\n\n"
        f"📝 **Daten ergänzen** nach dem Scan:\n"
        f"  `Raum: Heizungskeller`\n"
        f"  `Leistung: 5.5` (kW) oder `Leistung: 750W`\n"
        f"  `Laufzeit: 8` (h/Tag)",
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def abbrechen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bricht die Registrierung ab."""
    await update.message.reply_text("Registrierung abgebrochen.")
    return ConversationHandler.END


def get_start_handler():
    """Erstellt den ConversationHandler für /start."""
    return ConversationHandler(
        entry_points=[CommandHandler("start", start_command)],
        states={
            WARTE_AUF_PASSWORT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, passwort_eingabe)
            ],
            WARTE_AUF_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, name_eingabe)
            ],
        },
        fallbacks=[CommandHandler("abbrechen", abbrechen)],
    )
