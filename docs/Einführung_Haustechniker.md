# Typenschild-Scanner – Einführung für Haustechniker

## Willkommen!

Der **Typenschild-Scanner** ist ein Telegram-Bot, der Ihnen die Erfassung elektrischer Verbraucher in Gebäuden deutlich erleichtert. Statt mühsam von Hand Daten von Typenschildern abzuschreiben, fotografieren Sie das Typenschild einfach mit Ihrem Smartphone – die **Künstliche Intelligenz** (KI) liest automatisch alle relevanten Daten aus und speichert sie in einer Datenbank. Am Ende erhalten Sie einen professionellen PDF-Bericht und eine CSV-Datei zum Import in Excel.

---

## Inhaltsverzeichnis

1. [Was Sie brauchen](#1-was-sie-brauchen)
2. [Erste Schritte – Registrierung](#2-erste-schritte--registrierung)
3. [Einen Standort anlegen](#3-einen-standort-anlegen)
4. [Adresse per GPS hinterlegen](#4-adresse-per-gps-hinterlegen)
5. [Typenschilder scannen](#5-typenschilder-scannen--der-kern-der-anwendung)
6. [Daten ergänzen und korrigieren](#6-daten-ergänzen-und-korrigieren)
7. [Laufzeit erfassen](#7-laufzeit-erfassen)
8. [Leistung nachtragen](#8-leistung-nachtragen)
9. [Notizen und Sprachnachrichten](#9-notizen-und-sprachnachrichten)
10. [Verbraucher-Übersicht und Suche](#10-verbraucher-übersicht-und-suche)
11. [Standort-Statistik](#11-standort-statistik)
12. [Berichte und Exporte](#12-berichte-und-exporte)
13. [Das Web-Dashboard](#13-das-web-dashboard)
14. [Zwischen Standorten wechseln](#14-zwischen-standorten-wechseln)
15. [Tipps für die Praxis](#15-tipps-für-die-praxis)
16. [Befehlsübersicht auf einen Blick](#16-befehlsübersicht-auf-einen-blick)
17. [Häufige Fragen (FAQ)](#17-häufige-fragen-faq)

---

## 1. Was Sie brauchen

- **Telegram** auf Ihrem Smartphone (kostenlos verfügbar für Android und iOS)
- Das **Zugangspasswort** zum Bot (erhalten Sie von Ihrem Vorgesetzten oder Administrator)
- Den **Link zum Bot** oder den Bot-Namen in der Telegram-Suche

Das ist alles. Keine zusätzliche App, keine Registrierung bei Drittanbietern.

---

## 2. Erste Schritte – Registrierung

### So melden Sie sich an:

1. Öffnen Sie den Bot in Telegram und tippen Sie auf **„Starten"** oder geben Sie den Befehl ein:
   ```
   /start
   ```

2. Der Bot fragt Sie nach dem **Passwort**. Geben Sie es ein und senden Sie die Nachricht.  
   > ⚠️ **Hinweis:** Ihre Passwort-Nachricht wird aus Sicherheitsgründen sofort automatisch gelöscht. Falls Sie das Passwort dreimal falsch eingeben, wird Ihr Zugang gesperrt. In diesem Fall wenden Sie sich an Ihren Administrator.

3. Anschließend werden Sie nach Ihrem **Namen** gefragt. Geben Sie Ihren Vor- und Nachnamen ein – dieser erscheint später in den Berichten.

4. **Fertig!** Sie sind registriert und können sofort loslegen.

Nach der Registrierung zeigt Ihnen der Bot eine Willkommensnachricht mit einer Übersicht der wichtigsten Funktionen.

---

## 3. Einen Standort anlegen

Bevor Sie Typenschilder scannen können, müssen Sie einen **Standort** anlegen. Ein Standort ist typischerweise ein Gebäude, eine Liegenschaft oder ein Gebäudeteil.

### So legen Sie einen Standort an:

Geben Sie folgenden Befehl ein, gefolgt vom Namen:

```
/standort Bürogebäude Berlin Mitte
```

Der Bot bestätigt die Anlage und setzt den neuen Standort automatisch als Ihren **aktiven Standort**. Alle folgenden Scans werden diesem Standort zugeordnet.

### Beispiele für sinnvolle Standort-Namen:
- `/standort Rathaus Neukölln`
- `/standort Kita Sonnenschein`
- `/standort Schulzentrum Halle A`
- `/standort Heizzentrale Nord`

> 💡 **Tipp:** Wählen Sie aussagekräftige Namen, damit Sie Standorte später leicht wiederfinden.

---

## 4. Adresse per GPS hinterlegen

Sie können dem Standort automatisch eine Adresse zuweisen, indem Sie Ihren **GPS-Standort** teilen. Das ist besonders praktisch, wenn Sie direkt vor Ort sind.

### So geht's:

1. Tippen Sie in Telegram auf das **📎 Büroklammer-Symbol** (Anhang)
2. Wählen Sie **„Standort"** bzw. **„Location"**
3. Senden Sie Ihren aktuellen Standort

Der Bot ermittelt automatisch die Adresse (Straße, Hausnummer, PLZ, Ort) über OpenStreetMap und hinterlegt sie beim aktiven Standort. Sie erhalten eine Bestätigung mit der erkannten Adresse.

> 📍 Die Adresse erscheint später in den PDF-Berichten und im Dashboard.

---

## 5. Typenschilder scannen – Der Kern der Anwendung

Das Scannen von Typenschildern ist die Hauptfunktion des Bots. Die Bedienung ist denkbar einfach:

### So scannen Sie ein Typenschild:

1. **Fotografieren** Sie das Typenschild mit Ihrer Smartphone-Kamera direkt in Telegram
2. **Senden** Sie das Foto an den Bot
3. **Warten** Sie kurz – der Bot zeigt „🔍 Analysiere Typenschild... ⚡"
4. **Ergebnis prüfen** – der Bot zeigt alle erkannten Daten an

### Was die KI erkennt:

Die KI analysiert Ihr Foto und liest folgende Daten aus:

| Feld | Beispiel |
|------|----------|
| **Gerätetyp** | Motor, Pumpe, Lüfter, Kompressor, Klimagerät, ... |
| **Hersteller** | Siemens, ABB, Grundfos, Bitzer, ... |
| **Modell** | 1LA7096-4AA10 |
| **Seriennummer** | SN-2024-1234567 |
| **Baujahr** | 2019 |
| **Leistung** | 5,5 kW oder 750 W |
| **Spannung** | 400 V |
| **Strom** | 11,2 A |
| **Frequenz** | 50 Hz |
| **Phasen** | 3 |
| **cos φ** | 0,85 |
| **Drehzahl** | 1450 U/min |
| **Effizienzklasse** | IE3 |
| **Schutzart** | IP55 |

### Die Vertrauensanzeige:

Neben dem Ergebnis zeigt der Bot eine **Vertrauensanzeige** an:

- 🟢 **Gut lesbar** – Die KI konnte die meisten Daten sicher erkennen
- 🟡 **Teilweise lesbar** – Einige Daten könnten ungenau sein, bitte prüfen
- 🔴 **Schlecht lesbar** – Viele Daten unsicher, manuelle Kontrolle empfohlen

### Tipps für gute Scan-Ergebnisse:

- 📸 Halten Sie die Kamera **gerade** auf das Typenschild
- 💡 Sorgen Sie für **ausreichend Licht** (ggf. Taschenlampe nutzen)
- 🔍 Das Typenschild sollte **bildschirmfüllend** fotografiert werden
- 🧹 Reinigen Sie verschmutzte oder verrostete Typenschilder wenn möglich
- 📐 Vermeiden Sie starke **Spiegelungen** und **Winkelverzerrungen**
- 🔄 Bei schlechter Erkennung: **Erneut fotografieren** aus anderem Winkel

> 💡 Insgesamt erkennt die KI **27 verschiedene Gerätetypen**, darunter Motoren, Pumpen, Lüfter, Kompressoren, Heizungen, Klimageräte, Transformatoren, Frequenzumrichter, Beleuchtung, Aufzüge und viele mehr.

---

## 6. Daten ergänzen und korrigieren

Nach dem Scan können Sie Daten ergänzen oder korrigieren. Alle folgenden Texteingaben beziehen sich immer auf den **zuletzt gescannten Verbraucher**.

### Raum/Standort zuweisen:

Ordnen Sie dem Gerät einen Raum zu:
```
Raum: Heizungskeller
```
```
Raum: Technikzentrale EG
```
```
Raum: Büro 3.14
```

### Bezeichnung / Name vergeben:

Geben Sie dem Gerät einen sprechenden Namen:
```
Name: Zuluft AHU 3
```
```
Name: Heizungspumpe Vorlauf
```
```
Bezeichnung: Abluftventilator Küche
```

> 💡 **Wichtig:** Schreiben Sie `Raum:` oder `Name:` immer mit Doppelpunkt, damit der Bot die Eingabe korrekt zuordnet. Diese Eingaben werden **nicht** als Notiz gespeichert, sondern direkt im entsprechenden Datenfeld.

---

## 7. Laufzeit erfassen

Direkt nach dem Scan zeigt der Bot **Schnellauswahl-Buttons** für die Laufzeit:

| Button | Bedeutung | Stunden/Tag |
|--------|-----------|-------------|
| ⏱ **1h/Werktag** | Gerät läuft nur kurzzeitig | 1 h |
| ⏰ **8h/Werktag** | Gerät läuft während der Arbeitszeit | 8 h |
| 🔄 **24/7** | Gerät läuft rund um die Uhr | 24 h |
| ✍️ **Freitext** | Individuelle Eingabe | Ihre Angabe |

**Tippen Sie einfach auf den passenden Button.**

Falls Sie „Freitext" wählen, geben Sie anschließend die Stundenzahl als Zahl ein, z. B.:
```
12
```

Sie können die Laufzeit auch jederzeit nachträglich per Text setzen:
```
Laufzeit: 16
```

> 📊 Aus der Laufzeit und der Leistung berechnet der Bot automatisch den **Tagesverbrauch in kWh**. Diese Angabe erscheint in Berichten, Exporten und im Dashboard.
>
> **Formel:** Verbrauch (kWh/Tag) = Leistung (kW) × Laufzeit (h/Tag)

---

## 8. Leistung nachtragen

Die Leistung wird auf drei Wegen ermittelt:

### Stufe 1: Automatisch vom Typenschild
Die KI liest die Leistung direkt vom Foto ab – das klappt in den meisten Fällen.

### Stufe 2: Automatische Berechnung
Falls keine Leistung erkennbar war, aber **Spannung** und **Strom** erkannt wurden, berechnet der Bot die Leistung automatisch:
- **1-phasig:** P = U × I × cos φ
- **3-phasig:** P = U × I × √3 × cos φ

### Stufe 3: KI-Vorschlag
Falls auch die Berechnung nicht möglich war, recherchiert eine zweite KI typische Leistungswerte anhand von Hersteller, Modell und Gerätetyp. Sie erhalten dann einen **Vorschlag mit Sicherheitsbewertung**:

- 🟢 **Hohe Sicherheit** – Wert sehr wahrscheinlich korrekt
- 🟡 **Mittlere Sicherheit** – Wert ist eine gute Schätzung
- 🔴 **Niedrige Sicherheit** – Wert ist eine grobe Annäherung

Sie können den Vorschlag per **Button übernehmen** oder selbst eingeben:
```
Leistung: 5.5
```
(wird als kW interpretiert)

```
Leistung: 750W
```
(wird als Watt interpretiert)

```
Leistung: 2.2kW
```
(wird als Kilowatt interpretiert)

---

## 9. Notizen und Sprachnachrichten

### Textnotizen:
Jeder freie Text, der **nicht** mit `Raum:`, `Name:`, `Leistung:` oder `Laufzeit:` beginnt, wird als **Notiz** zum letzten gescannten Gerät gespeichert:

```
Lager defekt, Austausch geplant Q2/2026
```
```
Riemenantrieb, 2x V-Belt
```
```
Gerät außer Betrieb seit 01/2025
```

Mehrere Notizen werden automatisch aneinandergehängt.

### Sprachnachrichten:
Sie können statt zu tippen auch einfach eine **Sprachnachricht** aufnehmen. Die KI transkribiert Ihre Sprache automatisch in Text und speichert sie als Notiz. Besonders praktisch, wenn Sie beide Hände voll haben!

> 🎤 Halten Sie einfach die Mikrofon-Taste in Telegram gedrückt und sprechen Sie Ihre Notiz.

---

## 10. Verbraucher-Übersicht und Suche

### Alle Verbraucher am Standort anzeigen:

```
/liste
```

Zeigt alle erfassten Verbraucher am aktiven Standort mit:
- Laufende Nummer
- Bezeichnung (falls vergeben)
- Gerätetyp
- Hersteller
- Leistung
- Effizienzklasse
- Raum

### Verbraucher suchen:

```
/suche Siemens
```
```
/suche Pumpe
```
```
/suche IE1
```
```
/suche Heizungskeller
```

Die Suche durchsucht alle Felder: Hersteller, Modell, Seriennummer, Gerätetyp, Effizienzklasse, Raum, Bezeichnung, Notizen und Baujahr. Es werden maximal 20 Treffer angezeigt.

---

## 11. Standort-Statistik

```
/status
```

Zeigt eine Zusammenfassung Ihres aktiven Standorts:
- Name des Standorts
- Anzahl erfasster Verbraucher
- **Gesamtleistung** aller Verbraucher in kW
- Verteilung nach Gerätetypen (z. B. „5× Motor, 3× Pumpe, 2× Lüfter")

---

## 12. Berichte und Exporte

### PDF-Bericht generieren:

```
/bericht
```

Der Bot erstellt einen **professionellen PDF-Bericht** mit:
- Standort-Informationen (Name, Adresse)
- Alle Verbraucher, gruppiert nach Gerätetyp
- Tabellarische Übersicht mit Hersteller, Modell, Leistung, Spannung, Strom, Effizienzklasse, Laufzeit, Verbrauch und Raum
- **KI-Analyse**: Zusammenfassung, Empfehlungen zur Energieeinsparung, Modernisierungsvorschläge

Der Bericht wird als PDF-Datei direkt im Chat gesendet und zusätzlich im System gespeichert.

### CSV-Export für Excel:

```
/export
```

Exportiert alle Verbraucher als **CSV-Datei** (kompatibel mit Excel, LibreOffice etc.) mit 21 Spalten:
- ID, Gerätetyp, Hersteller, Modell, Seriennummer, Baujahr
- Leistung (kW und W), Spannung, Strom, Frequenz, Phasen, cos φ, Drehzahl
- Effizienzklasse, Raum, Bezeichnung
- Laufzeit (h/Tag), Verbrauch (kWh/Tag)
- Notizen, Erfassungsdatum

> 💡 Die CSV-Datei verwendet Semikolon (;) als Trennzeichen und ist für den deutschen Excel-Import optimiert.

---

## 13. Das Web-Dashboard

Zusätzlich zum Telegram-Bot gibt es ein **Web-Dashboard**, das Sie im Browser aufrufen können. Die Adresse erhalten Sie von Ihrem Administrator.

### Funktionen des Dashboards:

- **Übersichtsseite**: Alle Standorte mit Statistiken auf einen Blick
- **Standort-Detailansicht**: Alle Verbraucher in einer interaktiven Tabelle
- **Filter**: Filtern nach Gerätetyp, Hersteller oder Effizienzklasse
- **Fotos ansehen**: Klick auf das Kamera-Symbol zeigt das Original-Typenschild-Foto
- **Bericht generieren**: Direkt aus dem Dashboard per Klick auf „Bericht generieren"
- **CSV-Export**: Download als CSV-Datei für Excel
- **Berichte herunterladen**: Alle bisherigen Berichte als PDF herunterladen

> 🖥️ Das Dashboard eignet sich besonders für die Auswertung am PC und zur Präsentation der Ergebnisse.

---

## 14. Zwischen Standorten wechseln

Wenn Sie mehrere Standorte angelegt haben, können Sie einfach wechseln:

```
/wechsel
```

Der Bot zeigt alle Ihre Standorte als **Buttons** an. Tippen Sie auf den gewünschten Standort – ab sofort werden alle Scans und Eingaben diesem Standort zugeordnet.

> 💡 Sie können beliebig viele Standorte anlegen und jederzeit zwischen ihnen wechseln.

---

## 15. Tipps für die Praxis

### Vor dem Rundgang:
1. ✅ Stellen Sie sicher, dass Telegram funktioniert und Sie im Bot angemeldet sind
2. ✅ Legen Sie den **Standort** an (`/standort Gebäudename`)
3. ✅ Teilen Sie Ihren **GPS-Standort** für die automatische Adresse
4. ✅ Laden Sie Ihr Smartphone ausreichend auf

### Während des Rundgangs:
1. 📸 Fotografieren Sie **jedes Typenschild** einzeln
2. ⏱ Wählen Sie direkt die **Laufzeit** per Button
3. 🏠 Geben Sie den **Raum** ein: `Raum: Keller Raum 0.12`
4. 📝 Ergänzen Sie Auffälligkeiten als **Notiz** oder **Sprachnachricht**
5. 🔄 Wiederholen Sie den Vorgang für jedes Gerät

### Nach dem Rundgang:
1. 📋 Prüfen Sie die Erfassung mit `/liste` oder `/status`
2. 📊 Erstellen Sie den **Bericht** mit `/bericht`
3. 📁 Laden Sie die **CSV-Datei** mit `/export` herunter
4. 🖥️ Nutzen Sie das **Dashboard** für die Detailauswertung

### Empfohlene Reihenfolge pro Gerät:
```
1. 📷 Foto senden
2. ⏱ Laufzeit-Button drücken
3. 💡 Ggf. Leistungsvorschlag bestätigen
4. Raum: Technikzentrale UG
5. Name: Umwälzpumpe Heizkreis 1
6. Ggf. Notiz: "Geräusche bei Volllast"
```

---

## 16. Befehlsübersicht auf einen Blick

| Befehl | Funktion |
|--------|----------|
| `/start` | Registrierung / Anmeldung |
| `/standort <Name>` | Neuen Standort anlegen |
| `/wechsel` | Standort wechseln |
| `/status` | Standort-Statistik anzeigen |
| `/liste` | Alle Verbraucher auflisten |
| `/suche <Begriff>` | Verbraucher suchen |
| `/bericht` | PDF-Bericht generieren |
| `/export` | CSV-Export erstellen |
| `/hilfe` | Hilfe und Befehlsübersicht |
| `/abbrechen` | Registrierung abbrechen |

### Texteingaben:

| Eingabe | Wirkung |
|---------|---------|
| `Raum: <Text>` | Raum zuweisen |
| `Name: <Text>` | Bezeichnung vergeben |
| `Laufzeit: <Zahl>` | Laufzeit in Stunden setzen |
| `Leistung: <Zahl>` | Leistung nachtragen (kW/W) |
| Beliebiger Text | Als Notiz speichern |
| 🎤 Sprachnachricht | Wird transkribiert und als Notiz gespeichert |
| 📷 Foto | Typenschild-Scan starten |
| 📍 GPS-Standort | Adresse zum Standort hinterlegen |

---

## 17. Häufige Fragen (FAQ)

### „Das Typenschild ist zu verschmutzt / verrostet – was tun?"
Versuchen Sie, das Schild soweit möglich zu reinigen. Fotografieren Sie es aus verschiedenen Winkeln und bei besserem Licht. Notfalls können Sie die Daten auch manuell ergänzen (z. B. `Leistung: 3.0`).

### „Ich habe ein Gerät doppelt gescannt – wie lösche ich es?"
Der Bot bietet nach dem Scan Bearbeitungs-Buttons an. Nutzen Sie den 🗑️ „Verwerfen"-Button, um einen fehlerhaften Scan zu löschen.

### „Kann ich Fotos nachträglich zu einem Gerät hinzufügen?"
Aktuell wird jedes Foto als neuer Scan verarbeitet. Planen Sie daher pro Gerät ein aussagekräftiges Foto.

### „Was bedeuten IE1, IE2, IE3, IE4?"
Das sind **Effizienzklassen** für Elektromotoren nach der internationalen Norm IEC 60034-30:
- **IE1** = Standard-Wirkungsgrad (veraltet)
- **IE2** = Hoher Wirkungsgrad
- **IE3** = Premium-Wirkungsgrad (seit 2015 Mindestanforderung für viele Motoren)
- **IE4** = Super-Premium-Wirkungsgrad

Ältere Bezeichnungen (EFF1, EFF2) werden automatisch umgerechnet:
- EFF1 → IE3
- EFF2 → IE2

### „Warum zeigt der Bot manchmal eine Leistung an, die nicht auf dem Typenschild steht?"
Wenn die KI die Leistung nicht direkt lesen konnte, versucht der Bot sie aus Spannung × Strom × cos φ zu berechnen. Falls auch das nicht gelingt, recherchiert eine zweite KI typische Werte anhand von Hersteller und Modell. Solche Vorschläge sind als Schätzung gekennzeichnet (🟢🟡🔴).

### „Ich arbeite an einem anderen Standort – wie wechsle ich?"
Geben Sie `/wechsel` ein und tippen Sie auf den gewünschten Standort.

### „Können mehrere Techniker am selben Standort arbeiten?"
Ja! Jeder Techniker hat seinen eigenen Bot-Zugang, kann aber auf dieselben Standorte zugreifen. Die Scans aller Techniker fließen in dieselbe Datenbank.

### „Wo werden meine Daten gespeichert?"
Alle Daten (Fotos, Datenbank, Berichte) werden auf dem Server Ihres Unternehmens gespeichert – nicht bei Telegram oder OpenAI. Die KI-Analyse erfolgt über die OpenAI-API, dabei wird nur das Foto zur Analyse übertragen.

### „Kann ich den Bot auch offline nutzen?"
Nein, der Bot benötigt eine Internetverbindung für die KI-Analyse und die Kommunikation über Telegram. Stellen Sie sicher, dass Sie am Einsatzort Mobilfunkempfang haben.

---

## Noch Fragen?

Geben Sie im Bot jederzeit `/hilfe` ein, um eine Kurzübersicht aller Befehle zu erhalten. Bei technischen Problemen wenden Sie sich an Ihren Administrator.

**Viel Erfolg bei der Erfassung!** 🔧⚡
