"""Keyboard-Layouts für Inline-Buttons."""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def standort_auswahl_keyboard(standorte):
    """Erstellt Inline-Buttons zur Standortauswahl."""
    buttons = [
        [InlineKeyboardButton(s.name, callback_data=f"standort_{s.id}")]
        for s in standorte
    ]
    return InlineKeyboardMarkup(buttons)


def bestaetigung_keyboard(verbraucher_id: int):
    """Erstellt Bestätigungs-Buttons nach Typenschild-Scan."""
    buttons = [
        [
            InlineKeyboardButton("✅ Stimmt", callback_data=f"ok_{verbraucher_id}"),
            InlineKeyboardButton("✏️ Bearbeiten", callback_data=f"edit_{verbraucher_id}"),
        ],
        [
            InlineKeyboardButton("🗑️ Verwerfen", callback_data=f"del_{verbraucher_id}"),
        ],
    ]
    return InlineKeyboardMarkup(buttons)


def laufzeit_keyboard(verbraucher_id: int):
    """Erstellt Inline-Buttons zur Laufzeit-Auswahl nach Scan."""
    buttons = [
        [
            InlineKeyboardButton("⏱ 1h/Werktag", callback_data=f"lz_1_{verbraucher_id}"),
            InlineKeyboardButton("⏰ 8h/Werktag", callback_data=f"lz_8_{verbraucher_id}"),
        ],
        [
            InlineKeyboardButton("🔄 24/7", callback_data=f"lz_24_{verbraucher_id}"),
            InlineKeyboardButton("✍️ Freitext", callback_data=f"lz_custom_{verbraucher_id}"),
        ],
    ]
    return InlineKeyboardMarkup(buttons)


def leistung_vorschlag_keyboard(verbraucher_id: int, watt: float = None, kw: float = None):
    """Erstellt Inline-Buttons für KI-Leistungsvorschlag."""
    if kw:
        label = f"✅ {kw} kW übernehmen"
        data = f"pw_kw_{kw}_{verbraucher_id}"
    elif watt:
        label = f"✅ {watt} W übernehmen"
        data = f"pw_w_{watt}_{verbraucher_id}"
    else:
        return None

    buttons = [
        [InlineKeyboardButton(label, callback_data=data)],
        [InlineKeyboardButton("✍️ Selbst eingeben", callback_data=f"pw_custom_{verbraucher_id}")],
    ]
    return InlineKeyboardMarkup(buttons)
