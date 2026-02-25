"""Handler für /bericht – PDF-Standort-Report generieren & senden."""
import os
import logging
from telegram import Update
from telegram.ext import ContextTypes

from db.database import get_session
from db.models import Benutzer, Standort, Verbraucher, Bericht
from core.pdf import generiere_pdf
from core.ki import generiere_report_text

logger = logging.getLogger(__name__)


async def bericht_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generiert einen PDF-Standort-Report und sendet ihn im Chat."""
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
        standort_id = standort.id
        techniker_name = benutzer.name

        # Verbraucher laden
        verbraucher_liste = (
            session.query(Verbraucher)
            .filter_by(standort_id=standort_id)
            .order_by(Verbraucher.geraetetyp, Verbraucher.hersteller)
            .all()
        )

        if not verbraucher_liste:
            await update.message.reply_text(
                "📭 Keine Verbraucher am Standort erfasst.\n"
                "Sende zuerst Fotos von Typenschildern."
            )
            return

        # Daten aus Session extrahieren
        verbraucher_daten = []
        gesamt_kw = 0.0
        for v in verbraucher_liste:
            kw = v.leistung_kw or (v.leistung_w / 1000 if v.leistung_w else 0)
            gesamt_kw += kw

            verbraucher_daten.append({
                "id": v.id,
                "hersteller": v.hersteller or "–",
                "modell": v.modell or "–",
                "seriennummer": v.seriennummer or "–",
                "baujahr": v.baujahr,
                "geraetetyp": v.geraetetyp or "Sonstiges",
                "leistung_kw": v.leistung_kw,
                "leistung_w": v.leistung_w,
                "spannung_v": v.spannung_v or "–",
                "strom_a": v.strom_a or "–",
                "frequenz_hz": v.frequenz_hz,
                "drehzahl_rpm": v.drehzahl_rpm,
                "effizienzklasse": v.effizienzklasse or "–",
                "bezeichnung": v.bezeichnung or "–",
                "laufzeit_h": v.laufzeit_h,
                "verbrauch_kwh": round(kw * v.laufzeit_h, 2) if v.laufzeit_h and kw else None,
                "fotos": [f.dateipfad for f in v.fotos],
            })

    await update.message.reply_text("📄 Standort-Report wird erstellt... 🤖")

    # KI-Report generieren
    ki_report = generiere_report_text(verbraucher_daten)

    # PDF generieren
    try:
        pdf_pfad = generiere_pdf(
            standort_name=standort_name,
            techniker_name=techniker_name,
            verbraucher_daten=verbraucher_daten,
            ki_report=ki_report,
            gesamt_kw=gesamt_kw,
        )
    except Exception as e:
        logger.error(f"PDF-Erstellung fehlgeschlagen: {e}")
        await update.message.reply_text(f"❌ PDF-Erstellung fehlgeschlagen: {e}")
        return

    # Bericht in DB speichern
    with get_session() as session:
        bericht = Bericht(
            standort_id=standort_id,
            titel=f"Verbraucher-Report {standort_name}",
            pdf_pfad=pdf_pfad,
            anzahl_verbraucher=len(verbraucher_daten),
            gesamt_leistung_kw=gesamt_kw,
        )
        session.add(bericht)

    # PDF senden
    with open(pdf_pfad, "rb") as pdf_file:
        await update.message.reply_document(
            document=pdf_file,
            filename=os.path.basename(pdf_pfad),
            caption=(
                f"📊 Standort-Report: {standort_name}\n"
                f"⚡ {len(verbraucher_daten)} Verbraucher | {gesamt_kw:.1f} kW gesamt"
            ),
        )
