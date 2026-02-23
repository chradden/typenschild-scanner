# ⚡ Typenschild-Scanner

Telegram-Bot + Web-Dashboard zur automatischen Erfassung von **Typenschild-Daten** elektrischer Verbraucher per KI (GPT-4o Vision).

## Was macht die App?

1. **📷 Foto vom Typenschild** im Telegram-Bot senden
2. **🤖 KI liest automatisch aus:** Hersteller, Modell, kW, Volt, Ampere, Effizienzklasse, Seriennummer etc.
3. **💾 Speichert strukturiert** in der Datenbank
4. **📊 Web-Dashboard** zeigt alle erfassten Verbraucher mit Filtern
5. **📄 PDF-Reports** pro Standort mit Gesamtleistungsbilanz

## Features

- ⚡ **Typenschild-Erkennung** per GPT-4o Vision (kW, V, A, Hz, IE-Klasse, Schutzart...)
- 🎤 **Sprachnotizen** per Whisper transkribiert
- 📍 **Standort-Verwaltung** (Gebäude, Anlagen, Räume)
- 🔍 **Suche** über alle Verbraucher (Hersteller, Modell, Effizienzklasse...)
- 📊 **CSV-Export** aller technischen Daten
- 📄 **PDF-Standort-Report** mit KI-Empfehlungen (z.B. IE1→IE3 Austausch)
- 🔒 **Passwort-Schutz** für Bot und Dashboard
- 🐳 **Docker-Deployment** auf VPS

## Tech-Stack

| Komponente | Technologie |
|---|---|
| Bot | Telegram API (python-telegram-bot) |
| KI Vision | OpenAI GPT-4o |
| Sprache→Text | OpenAI Whisper |
| Backend | Python + FastAPI |
| Datenbank | SQLite (SQLAlchemy) |
| PDF | WeasyPrint + Jinja2 |
| Deployment | Docker |

## Telegram-Bot Befehle

| Befehl | Funktion |
|---|---|
| `/start` | Registrierung |
| `/standort <Name>` | Neuen Standort anlegen |
| `/wechsel` | Standort wechseln |
| `/status` | Übersicht (Geräte, Leistung) |
| `/liste` | Alle Verbraucher am Standort |
| `/suche <Begriff>` | Verbraucher suchen |
| `/bericht` | PDF-Report generieren |
| `/export` | CSV-Export |
| `/hilfe` | Alle Befehle |

## Schnellstart

```bash
# 1. Repository klonen
git clone https://github.com/chradden/typenschild-scanner.git
cd typenschild-scanner

# 2. .env konfigurieren
cp .env.example .env
nano .env  # Bot-Token und OpenAI-Key eintragen

# 3. Mit Docker starten
docker compose up -d --build

# Dashboard: http://localhost:8091
```

## Entwicklung (ohne Docker)

```bash
pip install -r requirements.txt
pip install "python-telegram-bot[job-queue]"

# Nur Dashboard (ohne Bot):
BOT_AKTIV=false python run.py
```

## Workflow

```
Techniker vor Ort                    System
──────────────────                   ──────
📷 Foto Typenschild    ─────────►    🤖 GPT-4o Vision analysiert
                                     💾 Daten in DB gespeichert
                                     📱 Bestätigung im Chat:
                                        "Siemens Motor, 5.5kW, 400V, IE3"

📝 "Raum: Heizungsraum" ────────►   💾 Raum-Zuordnung gespeichert

📷 Nächstes Typenschild ────────►   🤖 Nächster Verbraucher...

/bericht                ────────►   📄 PDF-Report mit allen Geräten
                                     + KI-Empfehlungen (IE1→IE3)
```
