"""Handler für /liste und /suche – Verbraucher auflisten und suchen."""
import logging
from telegram import Update
from telegram.ext import ContextTypes

from db.database import get_session
from db.models import Benutzer, Verbraucher

logger = logging.getLogger(__name__)


async def liste_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Listet alle Verbraucher am aktiven Standort auf."""
    telegram_id = update.effective_user.id

    with get_session() as session:
        benutzer = session.query(Benutzer).filter_by(telegram_id=telegram_id).first()
        if not benutzer:
            await update.message.reply_text("Bitte zuerst /start ausführen.")
            return

        if not benutzer.aktiver_standort_id:
            await update.message.reply_text(
                "Kein aktiver Standort. Erstelle einen mit /standort <Name>"
            )
            return

        verbraucher_liste = (
            session.query(Verbraucher)
            .filter_by(standort_id=benutzer.aktiver_standort_id)
            .order_by(Verbraucher.erstellt_am.desc())
            .all()
        )

        if not verbraucher_liste:
            await update.message.reply_text(
                "📭 Noch keine Verbraucher erfasst.\n"
                "Sende ein Foto eines Typenschilds zum Scannen."
            )
            return

        text = f"⚡ **Verbraucher am Standort** ({len(verbraucher_liste)} Stück)\n\n"

        for v in verbraucher_liste:
            leistung = ""
            if v.leistung_kw:
                leistung = f"{v.leistung_kw} kW"
            elif v.leistung_w:
                leistung = f"{v.leistung_w} W"

            zeile = f"**#{v.id}** "
            if v.bezeichnung:
                zeile += f"_{v.bezeichnung}_ – "
            zeile += f"{v.geraetetyp or '?'}"
            if v.hersteller:
                zeile += f" ({v.hersteller})"
            if leistung:
                zeile += f" | {leistung}"
            if v.effizienzklasse:
                zeile += f" | {v.effizienzklasse}"
            if v.raum:
                zeile += f" | 📍{v.raum}"

            text += zeile + "\n"

    # Telegram hat ein 4096-Zeichen-Limit
    if len(text) > 4000:
        text = text[:3990] + "\n\n... (Liste gekürzt)"

    await update.message.reply_text(text, parse_mode="Markdown")


async def suche_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sucht Verbraucher nach Stichwort."""
    telegram_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text(
            "Bitte Suchbegriff angeben:\n"
            "/suche <Begriff>\n\n"
            "Beispiel: /suche Siemens\n"
            "Beispiel: /suche Pumpe\n"
            "Beispiel: /suche IE1"
        )
        return

    suchbegriff = " ".join(context.args).lower()

    with get_session() as session:
        benutzer = session.query(Benutzer).filter_by(telegram_id=telegram_id).first()
        if not benutzer:
            await update.message.reply_text("Bitte zuerst /start ausführen.")
            return

        # Verbraucher am aktiven Standort laden und in Python filtern (SQLite hat kein ILIKE)
        if not benutzer.aktiver_standort_id:
            await update.message.reply_text(
                "Kein aktiver Standort. Erstelle einen mit /standort <Name>"
            )
            return

        alle = session.query(Verbraucher).filter_by(standort_id=benutzer.aktiver_standort_id).all()

        treffer = []
        for v in alle:
            suchfelder = " ".join(filter(None, [
                v.hersteller, v.modell, v.seriennummer,
                v.geraetetyp, v.effizienzklasse, v.schutzart,
                v.raum, v.bezeichnung, v.notizen,
                str(v.baujahr) if v.baujahr else None,
            ])).lower()

            if suchbegriff in suchfelder:
                treffer.append(v)

        if not treffer:
            await update.message.reply_text(
                f"🔍 Keine Treffer für \"{suchbegriff}\"."
            )
            return

        text = f"🔍 **{len(treffer)} Treffer** für \"{suchbegriff}\":\n\n"

        for v in treffer[:20]:  # Max 20 Ergebnisse
            leistung = ""
            if v.leistung_kw:
                leistung = f"{v.leistung_kw} kW"
            elif v.leistung_w:
                leistung = f"{v.leistung_w} W"

            zeile = f"**#{v.id}** {v.geraetetyp or '?'}"
            if v.hersteller:
                zeile += f" ({v.hersteller})"
            if v.modell:
                zeile += f" – {v.modell}"
            if leistung:
                zeile += f" | {leistung}"

            text += zeile + "\n"

    await update.message.reply_text(text, parse_mode="Markdown")
