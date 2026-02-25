"""Handler für Typenschild-Scan (Foto), Sprach- und Text-Notizen."""
import os
import json
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler

import config
from db.database import get_session
from db.models import Benutzer, Verbraucher, TypschildFoto
from core.ki import analysiere_typenschild, transkribiere_audio
from bot.keyboards import laufzeit_keyboard

logger = logging.getLogger(__name__)


async def foto_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verarbeitet eingehende Fotos als Typenschild-Scan."""
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

        jetzt = datetime.now()
        caption = update.message.caption or ""
        standort_id = benutzer.aktiver_standort_id
        benutzer_id = benutzer.id

        # Foto herunterladen
        photo = update.message.photo[-1]  # Höchste Auflösung
        file = await photo.get_file()

        foto_dir = os.path.join(
            config.UPLOAD_DIR,
            str(standort_id),
            jetzt.strftime("%Y-%m-%d"),
        )
        os.makedirs(foto_dir, exist_ok=True)

        dateipfad = os.path.join(
            foto_dir,
            f"scan_{jetzt.strftime('%H%M%S')}_{photo.file_unique_id}.jpg",
        )
        await file.download_to_drive(dateipfad)

    # KI-Analyse (außerhalb der DB-Session)
    await update.message.reply_text("🔍 Analysiere Typenschild... ⚡")

    ki_result = analysiere_typenschild(dateipfad)

    # Ergebnis in DB speichern
    with get_session() as session:
        verbraucher = Verbraucher(
            standort_id=standort_id,
            benutzer_id=benutzer_id,
            hersteller=ki_result.get("hersteller"),
            modell=ki_result.get("modell"),
            seriennummer=ki_result.get("seriennummer"),
            baujahr=ki_result.get("baujahr"),
            geraetetyp=ki_result.get("geraetetyp", "Sonstiges"),
            leistung_kw=ki_result.get("leistung_kw"),
            leistung_w=ki_result.get("leistung_w"),
            spannung_v=ki_result.get("spannung_v"),
            strom_a=ki_result.get("strom_a"),
            frequenz_hz=ki_result.get("frequenz_hz"),
            phasen=ki_result.get("phasen"),
            cos_phi=ki_result.get("cos_phi"),
            drehzahl_rpm=ki_result.get("drehzahl_rpm"),
            effizienzklasse=ki_result.get("effizienzklasse"),
            schutzart=ki_result.get("schutzart"),
            isolationsklasse=ki_result.get("isolationsklasse"),
            betriebsart=ki_result.get("betriebsart"),
            notizen=caption if caption else None,
            ki_rohdaten=json.dumps(ki_result, ensure_ascii=False),
            ki_lesbarkeit=ki_result.get("lesbarkeit", "mittel"),
            ki_vertrauen=ki_result.get("vertrauen", 0.5),
        )
        session.add(verbraucher)
        session.flush()

        foto_obj = TypschildFoto(
            verbraucher_id=verbraucher.id,
            dateipfad=dateipfad,
            ist_typschild=True,
            beschreibung=ki_result.get("zusaetzliche_daten"),
        )
        session.add(foto_obj)

        verbraucher_id = verbraucher.id

    # Fallback: Leistung aus Spannung × Strom × cos_phi berechnen
    if not ki_result.get("leistung_kw") and not ki_result.get("leistung_w"):
        try:
            spannung = ki_result.get("spannung_v", "") or ""
            strom = ki_result.get("strom_a", "") or ""
            cos_phi = ki_result.get("cos_phi")
            phasen = ki_result.get("phasen", 1) or 1

            # Bei Stern/Dreieck "230/400" → höheren Wert nehmen
            u = max(float(x) for x in spannung.replace(",", ".").split("/") if x.strip()) if spannung else None
            # Bei Strom "11.2/6.5" → zum höheren Spannungswert gehört der kleinere Strom
            strom_vals = [float(x) for x in strom.replace(",", ".").split("/") if x.strip()] if strom else []
            i = min(strom_vals) if len(strom_vals) > 1 else (strom_vals[0] if strom_vals else None)

            if u and i:
                phi = cos_phi if cos_phi else 0.85  # Annahme cos_phi=0.85 wenn unbekannt
                if phasen == 3:
                    p_w = u * i * 1.732 * phi
                else:
                    p_w = u * i * phi
                with get_session() as session:
                    v = session.get(Verbraucher, verbraucher_id)
                    if v:
                        v.leistung_w = round(p_w, 1)
                ki_result["leistung_w"] = round(p_w, 1)
                ki_result["_leistung_berechnet"] = True
        except (ValueError, TypeError):
            pass

    # Antwort formatieren
    antwort = _formatiere_scan_ergebnis(ki_result, verbraucher_id)
    await update.message.reply_text(antwort, parse_mode="Markdown")

    # Laufzeit-Abfrage per Inline-Buttons
    await update.message.reply_text(
        f"⏱ Wie lange läuft dieses Gerät täglich?",
        reply_markup=laufzeit_keyboard(verbraucher_id),
    )

    # Letzten Verbraucher merken für Notizen
    context.user_data["letzter_verbraucher_id"] = verbraucher_id


def _formatiere_scan_ergebnis(ki: dict, vid: int) -> str:
    """Formatiert das KI-Ergebnis als Telegram-Nachricht."""
    # Vertrauens-Indikator
    vertrauen = ki.get("vertrauen", 0)
    if vertrauen >= 0.8:
        qual = "🟢 Gut erkannt"
    elif vertrauen >= 0.5:
        qual = "🟡 Teilweise erkannt"
    else:
        qual = "🔴 Schlecht lesbar"

    text = f"⚡ **Typenschild erkannt** (#{vid})\n{qual}\n\n"

    # Identifikation
    if ki.get("hersteller"):
        text += f"🏭 Hersteller: {ki['hersteller']}\n"
    if ki.get("modell"):
        text += f"📋 Modell: {ki['modell']}\n"
    if ki.get("geraetetyp"):
        text += f"⚙️ Typ: {ki['geraetetyp']}\n"
    if ki.get("seriennummer"):
        text += f"🔢 S/N: {ki['seriennummer']}\n"
    if ki.get("baujahr"):
        text += f"📅 Baujahr: {ki['baujahr']}\n"

    # Elektrische Daten
    text += "\n"
    if ki.get("leistung_kw"):
        text += f"⚡ Leistung: {ki['leistung_kw']} kW"
        if ki.get("_leistung_berechnet"):
            text += " _(berechnet)_"
        text += "\n"
    elif ki.get("leistung_w"):
        text += f"⚡ Leistung: {ki['leistung_w']} W"
        if ki.get("_leistung_berechnet"):
            text += " _(berechnet)_"
        text += "\n"
    else:
        text += "⚠️ Leistung: _nicht erkannt_ → `Leistung: X` eingeben\n"
    if ki.get("spannung_v"):
        text += f"🔌 Spannung: {ki['spannung_v']} V\n"
    if ki.get("strom_a"):
        text += f"⚡ Strom: {ki['strom_a']} A\n"
    if ki.get("frequenz_hz"):
        text += f"〰️ Frequenz: {ki['frequenz_hz']} Hz\n"
    if ki.get("drehzahl_rpm"):
        text += f"🔄 Drehzahl: {ki['drehzahl_rpm']} U/min\n"
    if ki.get("cos_phi"):
        text += f"📐 cos φ: {ki['cos_phi']}\n"

    # Klassifikation
    if ki.get("effizienzklasse"):
        text += f"🏷️ Effizienz: {ki['effizienzklasse']}\n"
    if ki.get("schutzart"):
        text += f"🛡️ Schutzart: {ki['schutzart']}\n"

    text += "\n💡 Leistung nachtragen: `Leistung: 5.5` (kW) oder `Leistung: 750W`"
    text += "\n💡 Notiz hinzufügen: Einfach Text oder Sprache senden"

    return text


async def text_notiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verarbeitet Textnachrichten als Notiz zum letzten Verbraucher."""
    telegram_id = update.effective_user.id
    text = update.message.text

    letzter_id = context.user_data.get("letzter_verbraucher_id")
    if not letzter_id:
        await update.message.reply_text(
            "📝 Kein aktueller Verbraucher zum Ergänzen.\n"
            "Sende zuerst ein Foto eines Typenschilds."
        )
        return

    with get_session() as session:
        benutzer = session.query(Benutzer).filter_by(telegram_id=telegram_id).first()
        if not benutzer:
            await update.message.reply_text("Bitte zuerst /start ausführen.")
            return

        verbraucher = session.get(Verbraucher, letzter_id)
        if not verbraucher:
            await update.message.reply_text("Verbraucher nicht mehr gefunden.")
            return

        # Notiz anhängen
        if verbraucher.notizen:
            verbraucher.notizen += f"\n{text}"
        else:
            verbraucher.notizen = text

        # Prüfen ob Raum/Bezeichnung/Laufzeit angegeben
        text_lower = text.lower()
        if text_lower.startswith("raum:") or text_lower.startswith("raum "):
            verbraucher.raum = text.split(":", 1)[-1].strip() if ":" in text else text[5:].strip()
        elif text_lower.startswith("name:") or text_lower.startswith("bezeichnung:"):
            verbraucher.bezeichnung = text.split(":", 1)[-1].strip()
        elif text_lower.startswith("laufzeit:") or text_lower.startswith("laufzeit "):
            try:
                wert = text.split(":", 1)[-1].strip() if ":" in text else text[9:].strip()
                wert = wert.replace(",", ".").replace("h", "").replace("std", "").strip()
                verbraucher.laufzeit_h = float(wert)
            except ValueError:
                pass
        elif text_lower.startswith("leistung:") or text_lower.startswith("leistung "):
            try:
                wert = text.split(":", 1)[-1].strip() if ":" in text else text[9:].strip()
                wert_lower = wert.lower()
                if "kw" in wert_lower:
                    zahl = float(wert_lower.replace("kw", "").replace(",", ".").strip())
                    verbraucher.leistung_kw = zahl
                    verbraucher.leistung_w = None
                elif "w" in wert_lower:
                    zahl = float(wert_lower.replace("w", "").replace(",", ".").strip())
                    verbraucher.leistung_w = zahl
                    verbraucher.leistung_kw = None
                else:
                    # Ohne Einheit → als kW annehmen
                    zahl = float(wert.replace(",", ".").strip())
                    verbraucher.leistung_kw = zahl
                    verbraucher.leistung_w = None
            except ValueError:
                pass

    # Freitext-Laufzeit-Eingabe?
    lz_vid = context.user_data.pop("laufzeit_eingabe_fuer", None)
    if lz_vid:
        try:
            wert = text.replace(",", ".").replace("h", "").replace("std", "").strip()
            stunden = float(wert)
            with get_session() as session:
                v = session.get(Verbraucher, lz_vid)
                if v:
                    v.laufzeit_h = stunden
            await update.message.reply_text(f"✅ Laufzeit für #{lz_vid}: {stunden}h/Tag")
            return
        except ValueError:
            pass

    await update.message.reply_text(
        f"📝 Notiz zu Verbraucher #{letzter_id} hinzugefügt.\n"
        f"Weiter scannen: Nächstes Foto senden"
    )


async def sprach_notiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verarbeitet Sprachnachrichten als Notiz zum letzten Verbraucher."""
    telegram_id = update.effective_user.id

    letzter_id = context.user_data.get("letzter_verbraucher_id")
    if not letzter_id:
        await update.message.reply_text(
            "🎤 Kein aktueller Verbraucher zum Ergänzen.\n"
            "Sende zuerst ein Foto eines Typenschilds."
        )
        return

    with get_session() as session:
        benutzer = session.query(Benutzer).filter_by(telegram_id=telegram_id).first()
        if not benutzer:
            await update.message.reply_text("Bitte zuerst /start ausführen.")
            return

    # Sprachnachricht herunterladen
    jetzt = datetime.now()
    voice = update.message.voice
    file = await voice.get_file()

    voice_dir = os.path.join(config.UPLOAD_DIR, "voice")
    os.makedirs(voice_dir, exist_ok=True)
    voice_path = os.path.join(voice_dir, f"{telegram_id}_{jetzt.strftime('%Y%m%d_%H%M%S')}.ogg")
    await file.download_to_drive(voice_path)

    # Whisper-Transkription
    transkript = transkribiere_audio(voice_path)

    if not transkript:
        await update.message.reply_text("❌ Sprachnachricht konnte nicht transkribiert werden.")
        return

    # Notiz speichern
    with get_session() as session:
        verbraucher = session.get(Verbraucher, letzter_id)
        if verbraucher:
            if verbraucher.notizen:
                verbraucher.notizen += f"\n🎤 {transkript}"
            else:
                verbraucher.notizen = f"🎤 {transkript}"

    await update.message.reply_text(
        f"🎤 Notiz transkribiert und zu #{letzter_id} hinzugefügt:\n"
        f"\u201e{transkript[:150]}{'...' if len(transkript) > 150 else ''}\u201c"
    )


# ─── Bestätigungs-Callbacks ──────────────────────────────────────────────

async def bestaetigung_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback für Bestätigungs-Buttons nach Typenschild-Scan."""
    query = update.callback_query
    await query.answer()

    data = query.data
    aktion, vid_str = data.split("_", 1)
    vid = int(vid_str)

    if aktion == "ok":
        await query.edit_message_text(
            query.message.text + "\n\n✅ Daten bestätigt.",
            parse_mode="Markdown",
        )

    elif aktion == "del":
        with get_session() as session:
            verbraucher = session.get(Verbraucher, vid)
            if verbraucher:
                # Fotos löschen
                for foto in verbraucher.fotos:
                    if os.path.exists(foto.dateipfad):
                        os.remove(foto.dateipfad)
                    session.delete(foto)
                session.delete(verbraucher)

        await query.edit_message_text(f"🗑️ Verbraucher #{vid} gelöscht.")

    elif aktion == "edit":
        context.user_data["letzter_verbraucher_id"] = vid
        await query.edit_message_text(
            query.message.text + "\n\n✏️ Sende Korrekturen als Text.\n"
            "Beispiel: `Raum: Heizungskeller` oder `Bezeichnung: Pumpe P1`",
            parse_mode="Markdown",
        )


async def laufzeit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback für Laufzeit-Auswahl nach Typenschild-Scan."""
    query = update.callback_query
    await query.answer()

    data = query.data  # z.B. "lz_8_42" oder "lz_custom_42"
    parts = data.split("_")
    # parts: ["lz", stunden_oder_custom, verbraucher_id]
    wert = parts[1]
    vid = int(parts[2])

    if wert == "custom":
        context.user_data["laufzeit_eingabe_fuer"] = vid
        await query.edit_message_text(
            "✍️ Bitte Laufzeit in Stunden/Tag als Text eingeben:\n"
            "Beispiel: `4.5` oder `12`",
            parse_mode="Markdown",
        )
        return

    stunden = float(wert)
    with get_session() as session:
        verbraucher = session.get(Verbraucher, vid)
        if verbraucher:
            verbraucher.laufzeit_h = stunden

    label = {"1": "1h/Werktag", "8": "8h/Werktag", "24": "24/7"}.get(wert, f"{wert}h")
    await query.edit_message_text(f"✅ Laufzeit für #{vid}: {label}")


def get_bestaetigung_callback_handler():
    """Erstellt den CallbackQueryHandler für Bestätigungen."""
    return CallbackQueryHandler(bestaetigung_callback, pattern=r"^(ok|edit|del)_\d+$")


def get_laufzeit_callback_handler():
    """Erstellt den CallbackQueryHandler für Laufzeit-Auswahl."""
    return CallbackQueryHandler(laufzeit_callback, pattern=r"^lz_")
