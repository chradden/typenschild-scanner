#!/usr/bin/env python3
"""Konvertiert die Einführungs-Markdown-Datei in ein schön formatiertes PDF."""

import markdown
from weasyprint import HTML

# Markdown einlesen
with open("docs/Einführung_Haustechniker.md", "r", encoding="utf-8") as f:
    md_content = f.read()

# Markdown → HTML
html_body = markdown.markdown(
    md_content,
    extensions=["tables", "fenced_code", "toc", "nl2br"],
)

# Vollständiges HTML-Dokument mit professionellem CSS
html_doc = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<style>
@page {{
    size: A4;
    margin: 2.2cm 2cm 2.5cm 2cm;
    @bottom-center {{
        content: "Seite " counter(page) " von " counter(pages);
        font-size: 9pt;
        color: #888;
        font-family: 'Segoe UI', Arial, Helvetica, sans-serif;
    }}
    @top-right {{
        content: "Typenschild-Scanner";
        font-size: 8pt;
        color: #aaa;
        font-family: 'Segoe UI', Arial, Helvetica, sans-serif;
    }}
}}

@page :first {{
    @top-right {{ content: none; }}
    @bottom-center {{ content: none; }}
}}

* {{
    box-sizing: border-box;
}}

body {{
    font-family: 'Segoe UI', Arial, Helvetica, sans-serif;
    font-size: 10.5pt;
    line-height: 1.55;
    color: #222;
    max-width: 100%;
}}

/* Titelseite */
h1 {{
    font-size: 26pt;
    color: #1a5276;
    border-bottom: 4px solid #2e86c1;
    padding-bottom: 14px;
    margin-top: 60px;
    margin-bottom: 8px;
    font-weight: 700;
    letter-spacing: -0.5px;
}}

/* Untertitel-Effekt für den ersten Absatz */
h1 + h2 {{
    margin-top: 0;
}}

h2 {{
    font-size: 16pt;
    color: #1a5276;
    border-bottom: 2px solid #d4e6f1;
    padding-bottom: 6px;
    margin-top: 32px;
    margin-bottom: 12px;
    font-weight: 600;
    page-break-after: avoid;
}}

h3 {{
    font-size: 12.5pt;
    color: #2874a6;
    margin-top: 22px;
    margin-bottom: 8px;
    font-weight: 600;
    page-break-after: avoid;
}}

h4 {{
    font-size: 11pt;
    color: #2e86c1;
    margin-top: 16px;
    margin-bottom: 6px;
    font-weight: 600;
}}

p {{
    margin: 6px 0 10px 0;
    text-align: left;
    orphans: 3;
    widows: 3;
}}

/* Blockquotes als Info-Box */
blockquote {{
    background: #eaf2f8;
    border-left: 4px solid #2e86c1;
    padding: 12px 16px;
    margin: 14px 0;
    border-radius: 0 6px 6px 0;
    font-size: 10pt;
    color: #1a5276;
    page-break-inside: avoid;
}}

blockquote p {{
    margin: 4px 0;
}}

/* Tabellen */
table {{
    width: 100%;
    border-collapse: collapse;
    margin: 14px 0;
    font-size: 9.5pt;
    page-break-inside: avoid;
}}

thead {{
    background: #2e86c1;
    color: white;
}}

th {{
    padding: 9px 12px;
    text-align: left;
    font-weight: 600;
    font-size: 9.5pt;
    border: 1px solid #2874a6;
}}

td {{
    padding: 7px 12px;
    border: 1px solid #d5dbdb;
    vertical-align: top;
}}

tbody tr:nth-child(even) {{
    background: #f8f9fa;
}}

tbody tr:hover {{
    background: #eaf2f8;
}}

/* Code-Blöcke */
code {{
    background: #f0f3f5;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 9.5pt;
    color: #1a5276;
    border: 1px solid #dce1e4;
}}

pre {{
    background: #f7f9fb;
    border: 1px solid #d4e6f1;
    border-left: 4px solid #2e86c1;
    padding: 14px 18px;
    border-radius: 0 6px 6px 0;
    overflow-x: auto;
    font-size: 9.5pt;
    line-height: 1.5;
    margin: 12px 0;
    page-break-inside: avoid;
}}

pre code {{
    background: none;
    padding: 0;
    border: none;
    color: #2c3e50;
}}

/* Listen */
ul, ol {{
    margin: 8px 0;
    padding-left: 24px;
}}

li {{
    margin: 4px 0;
}}

/* Horizontale Linie */
hr {{
    border: none;
    border-top: 2px solid #d4e6f1;
    margin: 28px 0;
}}

/* Links */
a {{
    color: #2e86c1;
    text-decoration: none;
}}

/* Strong/Bold */
strong {{
    color: #1a5276;
    font-weight: 600;
}}

/* Seitenumbrüche vor H2 (außer dem ersten) */
h2 {{
    page-break-before: auto;
}}

/* Vermeide Umbrüche innerhalb zusammenhängender Blöcke */
h2 + h3,
h2 + p,
h3 + p,
h3 + table,
h3 + pre,
h3 + blockquote {{
    page-break-before: avoid;
}}

/* Inhaltsverzeichnis-Styling */
h2 + ol {{
    background: #f7f9fb;
    border: 1px solid #d4e6f1;
    border-radius: 8px;
    padding: 16px 16px 16px 40px;
    margin: 10px 0 20px 0;
}}

h2 + ol li {{
    margin: 3px 0;
}}

/* Deckblatt-Abstand */
h1:first-child {{
    margin-top: 120px;
    text-align: center;
    border-bottom: none;
    padding-bottom: 0;
}}

h1:first-child + h2 {{
    text-align: center;
    border-bottom: none;
    color: #5d6d7e;
    font-size: 14pt;
    font-weight: 400;
    margin-bottom: 40px;
}}
</style>
</head>
<body>
{html_body}
</body>
</html>"""

# PDF generieren
output_path = "docs/Einführung_Haustechniker.pdf"
HTML(string=html_doc).write_pdf(output_path)
print(f"✅ PDF erstellt: {output_path}")
