"""KI-Modul – OpenAI GPT Vision & Whisper für Typenschild-Erkennung."""
import json
import base64
import logging
from openai import OpenAI

import config

logger = logging.getLogger(__name__)

client = OpenAI(api_key=config.OPENAI_API_KEY)


# ─── Typenschild analysieren (Herzstück) ─────────────────────────────────

TYPENSCHILD_PROMPT = """Du bist ein Experte für elektrische Typenschilder und Leistungsschilder.
Analysiere dieses Foto eines Typenschilds und extrahiere ALLE lesbaren technischen Daten.

Antworte NUR mit validem JSON (kein Markdown, kein ```):
{
    "hersteller": "Name oder null",
    "modell": "Modellbezeichnung oder null",
    "seriennummer": "Seriennummer oder null",
    "baujahr": null oder Jahreszahl als Zahl,
    "geraetetyp": "Motor|Pumpe|Lüfter|Kompressor|Heizung|Klimagerät|Transformator|Frequenzumrichter|Kühlschrank|Spülmaschine|Waschmaschine|Trockner|Mikrowelle|Backofen|Herd|Kaffeemaschine|TV|Monitor|Drucker|Kopierer|Server|USV|Beleuchtung|Aufzug|Förderband|Schweissgerät|Ladegerät|Sonstiges",
    "leistung_kw": null oder Zahl,
    "leistung_w": null oder Zahl,
    "spannung_v": "Spannungsangabe als Text oder null",
    "strom_a": "Stromangabe als Text oder null",
    "frequenz_hz": null oder Zahl,
    "phasen": null oder 1 oder 3,
    "cos_phi": null oder Zahl,
    "drehzahl_rpm": null oder Zahl,
    "effizienzklasse": null oder "IE1" oder "IE2" oder "IE3" oder "IE4",
    "schutzart": null oder "IP...",
    "isolationsklasse": null oder "B" oder "F" oder "H",
    "betriebsart": null oder "S1" oder "S2" oder "S3" etc.,
    "zusaetzliche_daten": "Weitere lesbare Infos als Text oder null",
    "lesbarkeit": "gut|mittel|schlecht",
    "vertrauen": 0.0 bis 1.0
}

Regeln:
- Lies NUR was tatsächlich auf dem Typenschild steht
- Bei unleserlichen Feldern: null setzen
- Spannung und Strom als Text, da oft Stern/Dreieck-Angaben (z.B. "230/400")
- Leistung: Wenn nur W angegeben, in leistung_w eintragen. Wenn kW, in leistung_kw
- vertrauen: Wie sicher bist du bei der Gesamterkennung? (0.0 = unsicher, 1.0 = perfekt lesbar)
- lesbarkeit: Gesamtqualität des Typenschilds
- geraetetyp: Bestimme den passendsten Typ anhand von Hersteller, Modell und Kontext.
  Beispiele: PHILIPS TV → "TV", Mikrowelle → "Mikrowelle", Kopierer/MFP → "Kopierer",
  Siemens 1LE... → "Motor", Grundfos → "Pumpe". Nutze "Sonstiges" nur wenn kein Typ passt.
- Erfinde KEINE Daten – lieber null als falsch"""


def analysiere_typenschild(dateipfad: str) -> dict:
    """Analysiert ein Typenschild-Foto per GPT-4o Vision und extrahiert technische Daten."""
    try:
        with open(dateipfad, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": TYPENSCHILD_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}",
                                "detail": "high",  # Hohe Auflösung für Typenschilder
                            },
                        },
                    ],
                }
            ],
            max_tokens=800,
            temperature=0.1,
        )
        result = json.loads(response.choices[0].message.content)
        return result

    except json.JSONDecodeError as e:
        logger.error(f"KI-Antwort kein valides JSON: {e}")
        return _leeres_ergebnis("JSON-Parse-Fehler")
    except Exception as e:
        logger.error(f"Typenschild-Analyse fehlgeschlagen: {e}")
        return _leeres_ergebnis(str(e))


def _leeres_ergebnis(fehler: str = "") -> dict:
    """Gibt ein leeres Ergebnis-Dict zurück."""
    return {
        "hersteller": None,
        "modell": None,
        "seriennummer": None,
        "baujahr": None,
        "geraetetyp": "Sonstiges",
        "leistung_kw": None,
        "leistung_w": None,
        "spannung_v": None,
        "strom_a": None,
        "frequenz_hz": None,
        "phasen": None,
        "cos_phi": None,
        "drehzahl_rpm": None,
        "effizienzklasse": None,
        "schutzart": None,
        "isolationsklasse": None,
        "betriebsart": None,
        "zusaetzliche_daten": fehler,
        "lesbarkeit": "schlecht",
        "vertrauen": 0.0,
    }


# ─── Sprachnachricht transkribieren ──────────────────────────────────────

def transkribiere_audio(dateipfad: str) -> str:
    """Transkribiert eine Audiodatei per Whisper."""
    try:
        with open(dateipfad, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="de",
            )
        return response.text
    except Exception as e:
        logger.error(f"Whisper-Transkription fehlgeschlagen: {e}")
        return ""


# ─── Standort-Report generieren ──────────────────────────────────────────

REPORT_PROMPT = """Du bist ein Elektro-Fachingenieur. Erstelle aus den folgenden Verbraucher-Daten
einen strukturierten Standort-Report.

Struktur:
1. Zusammenfassung (Anzahl Geräte, Gesamtleistung, Standort)
2. Verbraucher nach Gerätetyp gruppiert (Motor, Pumpe, Lüfter, etc.)
   - Für jeden Verbraucher: Hersteller, Modell, Leistung, Spannung, Effizienzklasse
3. Effizienzklassen-Übersicht (Wie viele IE1, IE2, IE3, IE4?)
4. Empfehlungen (z.B. "5 Motoren mit IE1 – Austausch gegen IE3 empfohlen")
5. Gesamtleistungsbilanz

Regeln:
- Professioneller, sachlicher Stil
- Verwende KEIN Markdown mit ** – nutze einfachen Text mit Aufzählungszeichen (•)
- Erfinde KEINE Daten – nur was in den Verbraucherdaten steht
- Antworte auf Deutsch

Verbraucher-Daten:
{verbraucher}"""


def generiere_report_text(verbraucher_liste: list[dict]) -> str:
    """Generiert einen strukturierten Report-Text aus Verbraucher-Daten per GPT."""
    verbraucher_text = ""
    for i, v in enumerate(verbraucher_liste, 1):
        verbraucher_text += f"[Nr. {i}] "
        verbraucher_text += f"Typ: {v.get('geraetetyp', '?')}, "
        verbraucher_text += f"Hersteller: {v.get('hersteller', '?')}, "
        verbraucher_text += f"Modell: {v.get('modell', '?')}, "

        if v.get("leistung_kw"):
            verbraucher_text += f"Leistung: {v['leistung_kw']} kW, "
        elif v.get("leistung_w"):
            verbraucher_text += f"Leistung: {v['leistung_w']} W, "

        if v.get("spannung_v"):
            verbraucher_text += f"Spannung: {v['spannung_v']} V, "
        if v.get("strom_a"):
            verbraucher_text += f"Strom: {v['strom_a']} A, "
        if v.get("effizienzklasse"):
            verbraucher_text += f"Effizienz: {v['effizienzklasse']}, "
        if v.get("raum"):
            verbraucher_text += f"Raum: {v['raum']}, "
        if v.get("bezeichnung"):
            verbraucher_text += f"Bezeichnung: {v['bezeichnung']}, "

        verbraucher_text = verbraucher_text.rstrip(", ") + "\n"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": REPORT_PROMPT.format(verbraucher=verbraucher_text),
                },
            ],
            temperature=0.2,
            max_tokens=2000,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"KI-Report-Erstellung fehlgeschlagen: {e}")
        return ""
