"""PDF-Generierung für Standort-Reports."""
import os
import markdown
from datetime import date, datetime
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

import config

# Jinja2 Template-Umgebung
TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))


def generiere_pdf(
    standort_name: str,
    techniker_name: str,
    verbraucher_daten: list[dict],
    ki_report: str = "",
    gesamt_kw: float = 0.0,
) -> str:
    """
    Generiert einen PDF-Standort-Report.

    Returns:
        Pfad zur generierten PDF-Datei.
    """
    template = env.get_template("standort_report.html")

    # Foto-Pfade absolut machen
    for v in verbraucher_daten:
        if v.get("fotos"):
            v["fotos_abs"] = [os.path.abspath(f) for f in v["fotos"]]
        else:
            v["fotos_abs"] = []

    # KI-Report: Markdown → HTML konvertieren
    ki_report_html = ""
    if ki_report:
        ki_report_html = markdown.markdown(
            ki_report,
            extensions=["tables", "sane_lists"],
        )

    # Nach Gerätetyp gruppieren
    nach_typ = {}
    for v in verbraucher_daten:
        typ = v.get("geraetetyp", "Sonstiges")
        if typ not in nach_typ:
            nach_typ[typ] = []
        nach_typ[typ].append(v)

    html_content = template.render(
        standort_name=standort_name,
        techniker=techniker_name,
        datum=datetime.now().strftime("%d.%m.%Y"),
        verbraucher=verbraucher_daten,
        nach_typ=nach_typ,
        ki_report=ki_report_html,
        gesamt_kw=gesamt_kw,
        anzahl=len(verbraucher_daten),
        erstellt_am=datetime.now().strftime("%d.%m.%Y %H:%M"),
    )

    # Output-Verzeichnis vorbereiten
    os.makedirs(config.PDF_OUTPUT_DIR, exist_ok=True)

    # Dateiname
    safe_name = standort_name.replace(" ", "_").replace("/", "-")
    dateiname = f"Verbraucher_Report_{safe_name}_{datetime.now().strftime('%Y-%m-%d_%H%M')}.pdf"
    pdf_pfad = os.path.join(config.PDF_OUTPUT_DIR, dateiname)

    # PDF generieren
    HTML(string=html_content, base_url=".").write_pdf(pdf_pfad)

    return pdf_pfad
