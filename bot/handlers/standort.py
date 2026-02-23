"""Handler für /standort, /wechsel, /status, /hilfe – Standortverwaltung."""
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler

from db.database import get_session
from db.models import Benutzer, Standort, Verbraucher
from bot.keyboards import standort_auswahl_keyboard


async def standort_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Neuen Standort anlegen: /standort <Name>"""
    telegram_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text(
            "Bitte gib einen Standortnamen an:\n"
            "/standort <Name>\n\n"
            "Beispiel: /standort Bürogebäude Schönhauser Allee 45"
        )
        return

    standortname = " ".join(context.args)

    with get_session() as session:
        benutzer = session.query(Benutzer).filter_by(telegram_id=telegram_id).first()
        if not benutzer:
            await update.message.reply_text("Bitte zuerst /start ausführen.")
            return

        standort = Standort(name=standortname)
        session.add(standort)
        session.flush()

        benutzer.aktiver_standort_id = standort.id

    await update.message.reply_text(
        f"✅ Standort \"{standortname}\" angelegt und aktiviert.\n\n"
        f"Du kannst jetzt Typenschilder scannen:\n"
        f"📷 Foto vom Typenschild senden → KI liest die Daten aus\n"
        f"🎤 Sprachnachricht → Zusätzliche Notizen diktieren\n"
        f"📝 Text → Ergänzungen eingeben\n\n"
        f"/liste – Alle erfassten Verbraucher\n"
        f"/bericht – Standort-Report als PDF"
    )


async def wechsel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Aktiven Standort wechseln."""
    telegram_id = update.effective_user.id

    with get_session() as session:
        benutzer = session.query(Benutzer).filter_by(telegram_id=telegram_id).first()
        if not benutzer:
            await update.message.reply_text("Bitte zuerst /start ausführen.")
            return

        standorte = session.query(Standort).all()

    if not standorte:
        await update.message.reply_text(
            "Noch keine Standorte vorhanden.\n"
            "Erstelle einen mit /standort <Name>"
        )
        return

    await update.message.reply_text(
        "Wähle einen Standort:",
        reply_markup=standort_auswahl_keyboard(standorte)
    )


async def standort_auswahl_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback für Inline-Button Standortauswahl."""
    query = update.callback_query
    await query.answer()

    standort_id = int(query.data.split("_")[1])
    telegram_id = update.effective_user.id

    with get_session() as session:
        benutzer = session.query(Benutzer).filter_by(telegram_id=telegram_id).first()
        standort = session.get(Standort, standort_id)

        if benutzer and standort:
            benutzer.aktiver_standort_id = standort_id
            name = standort.name
        else:
            await query.edit_message_text("Fehler: Standort nicht gefunden.")
            return

    await query.edit_message_text(f"✅ Aktiver Standort: \"{name}\"")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Zeigt Status: aktiver Standort & erfasste Verbraucher."""
    telegram_id = update.effective_user.id

    with get_session() as session:
        benutzer = session.query(Benutzer).filter_by(telegram_id=telegram_id).first()
        if not benutzer:
            await update.message.reply_text("Bitte zuerst /start ausführen.")
            return

        if not benutzer.aktiver_standort_id:
            await update.message.reply_text(
                "Kein aktiver Standort.\n"
                "Erstelle einen mit /standort <Name>"
            )
            return

        standort = session.get(Standort, benutzer.aktiver_standort_id)
        verbraucher_gesamt = (
            session.query(Verbraucher)
            .filter_by(standort_id=standort.id)
            .count()
        )

        # Gesamtleistung berechnen (kW + W/1000)
        from sqlalchemy import func
        sum_kw = (
            session.query(func.sum(Verbraucher.leistung_kw))
            .filter_by(standort_id=standort.id)
            .scalar()
        ) or 0
        sum_w = (
            session.query(func.sum(Verbraucher.leistung_w))
            .filter_by(standort_id=standort.id)
            .scalar()
        ) or 0
        gesamt_kw = sum_kw + sum_w / 1000

        # Nach Gerätetyp gruppieren
        typen = (
            session.query(Verbraucher.geraetetyp, func.count())
            .filter_by(standort_id=standort.id)
            .group_by(Verbraucher.geraetetyp)
            .all()
        )

    text = (
        f"📍 **Standort:** {standort.name}\n"
        f"📋 **Verbraucher:** {verbraucher_gesamt}\n"
        f"⚡ **Gesamtleistung:** {gesamt_kw:.1f} kW\n"
    )

    if typen:
        text += "\n📊 **Nach Gerätetyp:**\n"
        for typ, anzahl in typen:
            text += f"  • {typ or 'Unbekannt'}: {anzahl}\n"

    text += f"\n/liste – Alle Verbraucher anzeigen"

    await update.message.reply_text(text, parse_mode="Markdown")


async def hilfe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Zeigt alle verfügbaren Befehle."""
    text = (
        "⚡ **Typenschild-Scanner – Befehle**\n\n"
        "📷 **Foto senden** → Typenschild wird automatisch ausgelesen\n"
        "🎤 **Sprachnachricht** → Notizen zum letzten Gerät\n"
        "📝 **Text senden** → Ergänzungen zum letzten Gerät\n\n"
        "**Standort-Verwaltung:**\n"
        "/standort <Name> – Neuen Standort anlegen\n"
        "/wechsel – Standort wechseln\n"
        "/status – Übersicht aktueller Standort\n\n"
        "**Verbraucher:**\n"
        "/liste – Alle Verbraucher am Standort\n"
        "/suche <Begriff> – Verbraucher suchen\n\n"
        "**Berichte:**\n"
        "/bericht – Standort-Report als PDF\n"
        "/export – CSV-Export aller Verbraucher\n\n"
        "/hilfe – Diese Hilfe anzeigen"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


def get_standort_callback_handler():
    """Erstellt den CallbackQueryHandler für die Standortauswahl."""
    return CallbackQueryHandler(standort_auswahl_callback, pattern=r"^standort_\d+$")
