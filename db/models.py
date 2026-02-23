"""Datenmodell für den Typenschild-Scanner."""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, BigInteger, String, Text, Date,
    DateTime, Float, Boolean, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


# ─── Standorte (ersetzt "Projekte") ──────────────────────────────────────

class Standort(Base):
    __tablename__ = "standorte"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)          # z.B. "Bürogebäude Mitte"
    adresse = Column(String)
    gebaeude = Column(String)                      # z.B. "Hauptgebäude"
    etage = Column(String)                         # z.B. "UG", "EG", "1. OG"
    ansprechpartner = Column(String)
    erstellt_am = Column(DateTime, default=datetime.now)

    verbraucher = relationship("Verbraucher", back_populates="standort")


# ─── Benutzer ─────────────────────────────────────────────────────────────

class Benutzer(Base):
    __tablename__ = "benutzer"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    name = Column(String, nullable=False)
    rolle = Column(String, default="techniker")    # techniker, meister, ingenieur
    aktiver_standort_id = Column(Integer, ForeignKey("standorte.id"))
    erstellt_am = Column(DateTime, default=datetime.now)

    aktiver_standort = relationship("Standort")
    verbraucher = relationship("Verbraucher", back_populates="benutzer")


# ─── Verbraucher (Kernstück) ─────────────────────────────────────────────

class Verbraucher(Base):
    """Ein elektrischer Verbraucher mit Typenschild-Daten."""
    __tablename__ = "verbraucher"

    id = Column(Integer, primary_key=True, autoincrement=True)
    standort_id = Column(Integer, ForeignKey("standorte.id"), nullable=False)
    benutzer_id = Column(Integer, ForeignKey("benutzer.id"))

    # ── Typenschild-Identifikation ──
    hersteller = Column(String)                    # z.B. "Siemens", "ABB", "WEG"
    modell = Column(String)                        # z.B. "1LE1003-1AB42"
    seriennummer = Column(String)
    baujahr = Column(Integer)
    geraetetyp = Column(String)                    # "Motor", "Pumpe", "Lüfter", "Kompressor"...

    # ── Elektrische Daten ──
    leistung_kw = Column(Float)                    # Nennleistung in kW
    leistung_w = Column(Float)                     # Alternativ in Watt
    spannung_v = Column(String)                    # z.B. "400" oder "230/400"
    strom_a = Column(String)                       # z.B. "11.2" oder "19.4/11.2"
    frequenz_hz = Column(Float)                    # 50 oder 60 Hz
    phasen = Column(Integer)                       # 1 oder 3
    cos_phi = Column(Float)                        # Leistungsfaktor
    drehzahl_rpm = Column(Integer)                 # Nenndrehzahl U/min

    # ── Klassifikation ──
    effizienzklasse = Column(String)               # IE1, IE2, IE3, IE4
    schutzart = Column(String)                     # IP55, IP44, IP65...
    isolationsklasse = Column(String)              # F, H, B...
    betriebsart = Column(String)                   # S1, S2, S3...

    # ── Zusätzliche Infos ──
    raum = Column(String)                          # "Heizungsraum", "Technikzentrale"
    bezeichnung = Column(String)                   # Eigene Bezeichnung, z.B. "Zuluft-Ventilator AHU3"
    notizen = Column(Text)                         # Freitext-Notizen

    # ── KI-Daten ──
    ki_rohdaten = Column(Text)                     # Vollständiges JSON der KI-Analyse
    ki_lesbarkeit = Column(String)                 # "gut", "mittel", "schlecht"
    ki_vertrauen = Column(Float)                   # 0.0 - 1.0

    erstellt_am = Column(DateTime, default=datetime.now)
    aktualisiert_am = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Beziehungen
    standort = relationship("Standort", back_populates="verbraucher")
    benutzer = relationship("Benutzer", back_populates="verbraucher")
    fotos = relationship("TypschildFoto", back_populates="verbraucher")


# ─── Fotos ────────────────────────────────────────────────────────────────

class TypschildFoto(Base):
    """Foto eines Typenschilds oder des Geräts selbst."""
    __tablename__ = "typschild_fotos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    verbraucher_id = Column(Integer, ForeignKey("verbraucher.id"), nullable=False)
    dateipfad = Column(String, nullable=False)
    ist_typschild = Column(Boolean, default=True)  # True = Typschild, False = Gerätefoto
    beschreibung = Column(Text)                    # KI-generierte Beschreibung
    erstellt_am = Column(DateTime, default=datetime.now)

    verbraucher = relationship("Verbraucher", back_populates="fotos")


# ─── Berichte ─────────────────────────────────────────────────────────────

class Bericht(Base):
    """Generierter Standort-Report als PDF."""
    __tablename__ = "berichte"

    id = Column(Integer, primary_key=True, autoincrement=True)
    standort_id = Column(Integer, ForeignKey("standorte.id"), nullable=False)
    titel = Column(String)                         # z.B. "Verbraucher-Report Bürogebäude"
    pdf_pfad = Column(String)
    anzahl_verbraucher = Column(Integer)
    gesamt_leistung_kw = Column(Float)
    erstellt_am = Column(DateTime, default=datetime.now)

    standort = relationship("Standort")
