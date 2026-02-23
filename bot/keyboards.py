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
