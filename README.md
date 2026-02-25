# ⚡ Typenschild-Scanner

Telegram-Bot + Web-Dashboard zur automatischen Erfassung von **Typenschild-Daten** elektrischer Verbraucher per KI (GPT-4o Vision).

## Was macht die App?

1. **📷 Foto vom Typenschild** im Telegram-Bot senden
2. **🤖 KI liest automatisch aus:** Hersteller, Modell, kW, Volt, Ampere, Effizienzklasse, Seriennummer etc.
3. **💾 Speichert strukturiert** in der Datenbank
4. **📊 Web-Dashboard** zeigt alle erfassten Verbraucher mit Filtern
5. **📄 PDF-Reports** pro Standort mit Gesamtleistungsbilanz und KI-Empfehlungen

## Features

### Typenschild-Erkennung
- ⚡ **GPT-4o Vision** liest Typenschilder automatisch aus (kW, V, A, Hz, IE-Klasse...)
- 🏷️ **27 Gerätetypen** werden erkannt (Motor, Pumpe, TV, Mikrowelle, Kopierer, Server, Aufzug u.v.m.)
- 🔋 **Leistungs-Ermittlung** in 3 Stufen:
  1. Direkt vom Typenschild lesen
  2. Automatische Berechnung aus Spannung × Strom × cos φ
  3. KI-Recherche nach typischen Werten anhand Hersteller/Modell (mit Übernahme-Button)
- 🏷️ **Effizienzklasse** wird aktiv gesucht (IE1–IE4, EFF1/EFF2-Mapping)

### Standort-Verwaltung
- 📍 **GPS-Standort teilen** → Adresse wird automatisch per Reverse Geocoding (OpenStreetMap) hinterlegt
- 🏢 Mehrere Standorte verwalten und schnell wechseln

### Erfassung & Ergänzung
- 🎤 **Sprachnotizen** per Whisper transkribiert
- ⏱️ **Laufzeit-Abfrage** per Inline-Buttons nach jedem Scan (1h/Werktag, 8h/Werktag, 24/7, Freitext)
- 📝 **Manuelle Nachtragung** per Textbefehl: `Leistung: 60W`, `Laufzeit: 8`, `Raum: Heizungskeller`
- 📊 **Verbrauch** wird automatisch berechnet: Leistung (kW) × Laufzeit (h/Tag) = kWh/Tag

### Berichte & Export
- 📄 **PDF-Standort-Report** mit KI-Analyse und Empfehlungen (z.B. IE1→IE3 Austausch)
- 📊 **CSV-Export** mit allen technischen Daten inkl. Laufzeit und Verbrauch
- 🌐 **Dashboard-Report** – PDF direkt im Web-Dashboard generieren

### Sicherheit & Deployment
- 🔒 **Passwort-Schutz** für Bot und Dashboard (optional)
- 🐳 **Docker-Deployment** auf VPS
- 🌐 **Caddy Reverse Proxy** mit automatischem SSL

## Tech-Stack

| Komponente | Technologie |
|---|---|
| Bot | Telegram API (python-telegram-bot 21.6) |
| KI Vision | OpenAI GPT-4o |
| KI Reports | OpenAI GPT-4o-mini |
| Sprache→Text | OpenAI Whisper |
| Backend | Python 3.12 + FastAPI |
| Datenbank | SQLite (SQLAlchemy 2.0) |
| PDF | WeasyPrint + Jinja2 |
| Geocoding | OpenStreetMap Nominatim (kostenlos) |
| Deployment | Docker + Caddy |

## Telegram-Bot Befehle

| Befehl | Funktion |
|---|---|
| `/start` | Registrierung (mit optionalem Passwortschutz) |
| `/standort <Name>` | Neuen Standort anlegen |
| `/wechsel` | Standort wechseln |
| `/status` | Übersicht (Geräte, Leistung, Typen) |
| `/liste` | Alle Verbraucher am Standort |
| `/suche <Begriff>` | Verbraucher suchen |
| `/bericht` | PDF-Report generieren & senden |
| `/export` | CSV-Export aller Verbraucher |
| `/hilfe` | Alle Befehle |

### Zusätzliche Eingaben (nach Scan)

| Eingabe | Wirkung |
|---|---|
| 📷 Foto senden | Typenschild scannen |
| 📍 Standort teilen | Adresse automatisch hinterlegen |
| `Leistung: 5.5` | Leistung nachtragen (kW) |
| `Leistung: 750W` | Leistung nachtragen (Watt) |
| `Laufzeit: 8` | Laufzeit setzen (h/Tag) |
| `Raum: Heizungskeller` | Raum zuordnen |
| `Name: Zuluft AHU3` | Bezeichnung setzen |
| 🎤 Sprachnachricht | Notiz per Sprache diktieren |
| Freitext | Notiz zum letzten Gerät |

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

## Umgebungsvariablen

| Variable | Beschreibung | Default |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token (BotFather) | – (erforderlich) |
| `OPENAI_API_KEY` | OpenAI API Key | – (erforderlich) |
| `BOT_PASSWORT` | Zugangspasswort für den Bot | leer (kein Schutz) |
| `DASHBOARD_USER` | Dashboard Benutzername | `admin` |
| `DASHBOARD_PASSWORT` | Dashboard Passwort | leer (kein Schutz) |
| `BOT_AKTIV` | Bot starten? (`true`/`false`) | `true` |
| `DATABASE_URL` | SQLAlchemy DB-URL | `sqlite:///typenschild.db` |

## Entwicklung (ohne Docker)

```bash
pip install -r requirements.txt

# Bot + Dashboard starten:
python run.py

# Nur Dashboard (ohne Bot):
BOT_AKTIV=false python run.py
```

## VPS-Deployment

```bash
# Auf dem VPS:
cd /opt/typenschild-scanner
git pull
docker compose up -d --build

# Caddy Reverse Proxy (mit automatischem SSL):
# /etc/caddy/Caddyfile:
# scanner.example.de {
#     reverse_proxy localhost:8091
# }
```

## Projektstruktur

```
typenschild-scanner/
├── bot/                    # Telegram Bot
│   ├── handlers/           # Command & Message Handler
│   │   ├── start.py        # /start – Registrierung
│   │   ├── standort.py     # /standort, /wechsel, /status, GPS
│   │   ├── scan.py         # Foto-Scan, Notizen, Callbacks
│   │   ├── liste.py        # /liste, /suche
│   │   ├── bericht.py      # /bericht – PDF-Report
│   │   └── export.py       # /export – CSV-Export
│   ├── keyboards.py        # Inline-Keyboard Layouts
│   └── main.py             # Bot-Setup & Handler-Registrierung
├── core/                   # Kernlogik
│   ├── ki.py               # OpenAI GPT-4o Vision + Whisper + Leistungsschätzung
│   └── pdf.py              # PDF-Generierung mit WeasyPrint
├── db/                     # Datenbank
│   ├── database.py         # SQLAlchemy Session-Management
│   └── models.py           # Datenmodell (Standort, Verbraucher, Bericht...)
├── web/                    # Web-Dashboard
│   ├── app.py              # FastAPI Routen
│   ├── static/             # CSS
│   └── templates/          # HTML-Templates (Dashboard, Standort-Detail)
├── templates/              # PDF-Report Template
├── config.py               # Konfiguration aus .env
├── run.py                  # Hauptstartpunkt (Bot + Web)
├── Dockerfile              # Container-Build
├── docker-compose.yml      # Docker Compose
├── requirements.txt        # Python Dependencies
└── .env.example            # Vorlage für Umgebungsvariablen
```

## Workflow

```
Techniker vor Ort                    System
──────────────────                   ──────
📍 Standort teilen      ─────────►  🗺️ Adresse per GPS hinterlegt

📷 Foto Typenschild     ─────────►  🤖 GPT-4o Vision analysiert
                                     💾 Daten in DB gespeichert
                                     📱 Ergebnis im Chat:
                                        "Samsung Monitor, 60W, AC100-240V"
                                     ⏱️ Laufzeit-Buttons: 1h | 8h | 24/7

🔋 Leistung nicht lesbar ────────►  🤖 KI recherchiert typische Werte
                                     📱 "Vorschlag: 60W [✅ Übernehmen]"

📝 "Leistung: 750W"     ────────►  💾 Leistung manuell gesetzt

📷 Nächstes Typenschild  ────────►  🤖 Nächster Verbraucher...

/bericht                 ────────►  📄 PDF-Report mit allen Geräten
                                     + KI-Empfehlungen (IE1→IE3)

🌐 Dashboard             ────────►  📊 Tabelle, Filter, CSV-Export
                                     📄 Report direkt generieren
```
