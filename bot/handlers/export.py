"""Handler für /export – CSV-Export der Verbraucher."""
import csv
import io
import os
from datetime import date
from telegram import Update
from telegram.ext import ContextTypes

from db.database import get_session
from db.models import Benutzer, Standort, Verbraucher


async def export_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Exportiert alle Verbraucher des aktiven Standorts als CSV-Datei."""
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

        standort = session.get(Standort, benutzer.aktiver_standort_id)
        standort_name = standort.name

        verbraucher = (
            session.query(Verbraucher)
            .filter_by(standort_id=standort.id)
            .order_by(Verbraucher.geraetetyp, Verbraucher.hersteller)
            .all()
        )

        if not verbraucher:
            await update.message.reply_text("📭 Keine Verbraucher zum Exportieren.")
            return

        rows = []
        for v in verbraucher:
            rows.append({
                "ID": v.id,
                "Gerätetyp": v.geraetetyp or "",
                "Hersteller": v.hersteller or "",
                "Modell": v.modell or "",
                "Seriennummer": v.seriennummer or "",
                "Baujahr": v.baujahr or "",
                "Leistung_kW": v.leistung_kw or "",
                "Leistung_W": v.leistung_w or "",
                "Spannung_V": v.spannung_v or "",
                "Strom_A": v.strom_a or "",
                "Frequenz_Hz": v.frequenz_hz or "",
                "Phasen": v.phasen or "",
                "cos_phi": v.cos_phi or "",
                "Drehzahl_rpm": v.drehzahl_rpm or "",
                "Effizienzklasse": v.effizienzklasse or "",
                "Schutzart": v.schutzart or "",
                "Isolationsklasse": v.isolationsklasse or "",
                "Betriebsart": v.betriebsart or "",
                "Raum": v.raum or "",
                "Bezeichnung": v.bezeichnung or "",
                "Notizen": v.notizen or "",
                "Erfasst_am": v.erstellt_am.strftime("%d.%m.%Y %H:%M") if v.erstellt_am else "",
            })

    # CSV erstellen
    output = io.StringIO()
    if rows:
        writer = csv.DictWriter(output, fieldnames=rows[0].keys(), delimiter=";")
        writer.writeheader()
        writer.writerows(rows)

    safe_name = standort_name.replace(" ", "_")
    filename = f"Verbraucher_{safe_name}_{date.today().strftime('%Y-%m-%d')}.csv"

    csv_bytes = output.getvalue().encode("utf-8-sig")

    await update.message.reply_document(
        document=io.BytesIO(csv_bytes),
        filename=filename,
        caption=f"📊 {len(rows)} Verbraucher exportiert – {standort_name}",
    )
