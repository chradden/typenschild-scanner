"""FastAPI Web-Dashboard für Typenschild-Scanner."""
import os
import csv
import io
import secrets
import logging
from datetime import date, datetime
from fastapi import FastAPI, Request, Query, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import func

import config
from db.database import get_session
from db.models import Standort, Benutzer, Verbraucher, TypschildFoto, Bericht

logger = logging.getLogger(__name__)

app = FastAPI(title="Typenschild-Scanner Dashboard")
security = HTTPBasic()

# Static files & templates
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")

os.makedirs(STATIC_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATE_DIR)


# ─── Auth ─────────────────────────────────────────────────────────────────

async def auth_pruefen(request: Request):
    """Prüft HTTP Basic Auth, wenn DASHBOARD_PASSWORT gesetzt ist."""
    if not config.DASHBOARD_PASSWORT:
        return True

    # Manuell Authorization-Header parsen (kein Browser-Dialog wenn kein PW gesetzt)
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentifizierung erforderlich",
            headers={"WWW-Authenticate": "Basic"},
        )

    try:
        import base64
        scheme, credentials = auth_header.split(" ", 1)
        if scheme.lower() != "basic":
            raise ValueError("Ungültiges Schema")
        decoded = base64.b64decode(credentials).decode("utf-8")
        username, password = decoded.split(":", 1)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültige Authentifizierung",
            headers={"WWW-Authenticate": "Basic"},
        )

    korrekt_user = secrets.compare_digest(
        username.encode("utf-8"),
        config.DASHBOARD_USER.encode("utf-8"),
    )
    korrekt_pw = secrets.compare_digest(
        password.encode("utf-8"),
        config.DASHBOARD_PASSWORT.encode("utf-8"),
    )

    if not (korrekt_user and korrekt_pw):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falscher Benutzername oder Passwort",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True


# ─── Routen ───────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, auth=Depends(auth_pruefen)):
    """Hauptseite – Standortübersicht mit Statistiken."""
    with get_session() as session:
        standorte = session.query(Standort).all()
        standort_daten = []

        for s in standorte:
            anzahl = session.query(Verbraucher).filter_by(standort_id=s.id).count()
            anzahl_fotos = (
                session.query(TypschildFoto)
                .join(Verbraucher)
                .filter(Verbraucher.standort_id == s.id)
                .count()
            )

            gesamt_kw = (
                session.query(func.sum(Verbraucher.leistung_kw))
                .filter_by(standort_id=s.id)
                .scalar()
            ) or 0

            anzahl_berichte = session.query(Bericht).filter_by(standort_id=s.id).count()

            # Letzte Erfassungen
            letzte = (
                session.query(Verbraucher)
                .filter_by(standort_id=s.id)
                .order_by(Verbraucher.erstellt_am.desc())
                .limit(3)
                .all()
            )

            standort_daten.append({
                "id": s.id,
                "name": s.name,
                "adresse": s.adresse or "–",
                "anzahl_verbraucher": anzahl,
                "anzahl_fotos": anzahl_fotos,
                "gesamt_kw": gesamt_kw,
                "anzahl_berichte": anzahl_berichte,
                "letzte_verbraucher": [
                    {
                        "geraetetyp": v.geraetetyp or "?",
                        "hersteller": v.hersteller or "–",
                        "leistung_kw": v.leistung_kw,
                    }
                    for v in letzte
                ],
            })

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "standorte": standort_daten,
        "titel": "Typenschild-Scanner",
    })


@app.get("/standort/{standort_id}", response_class=HTMLResponse)
async def standort_detail(
    request: Request,
    standort_id: int,
    typ: str = Query(None, description="Filter: Gerätetyp"),
    hersteller: str = Query(None, description="Filter: Hersteller"),
    effizienz: str = Query(None, description="Filter: IE1|IE2|IE3|IE4"),
    auth=Depends(auth_pruefen),
):
    """Detailansicht eines Standorts mit Verbrauchern."""
    with get_session() as session:
        standort = session.get(Standort, standort_id)
        if not standort:
            return HTMLResponse("<h1>Standort nicht gefunden</h1>", status_code=404)

        standort_info = {
            "id": standort.id,
            "name": standort.name,
            "adresse": standort.adresse or "–",
            "gebaeude": standort.gebaeude or "–",
            "ansprechpartner": standort.ansprechpartner or "–",
        }

        # Verbraucher abfragen
        query = session.query(Verbraucher).filter_by(standort_id=standort_id)
        if typ:
            query = query.filter(Verbraucher.geraetetyp == typ)
        if hersteller:
            query = query.filter(Verbraucher.hersteller == hersteller)
        if effizienz:
            query = query.filter(Verbraucher.effizienzklasse == effizienz)

        verbraucher = query.order_by(Verbraucher.geraetetyp, Verbraucher.hersteller).all()

        verbraucher_daten = []
        gesamt_kw = 0.0
        for v in verbraucher:
            kw = v.leistung_kw or (v.leistung_w / 1000 if v.leistung_w else 0)
            gesamt_kw += kw

            fotos = [{"id": f.id, "dateipfad": f.dateipfad} for f in v.fotos]
            verbraucher_daten.append({
                "id": v.id,
                "hersteller": v.hersteller or "–",
                "modell": v.modell or "–",
                "seriennummer": v.seriennummer or "–",
                "baujahr": v.baujahr,
                "geraetetyp": v.geraetetyp or "Sonstiges",
                "leistung_kw": v.leistung_kw,
                "leistung_w": v.leistung_w,
                "spannung_v": v.spannung_v or "–",
                "strom_a": v.strom_a or "–",
                "frequenz_hz": v.frequenz_hz,
                "drehzahl_rpm": v.drehzahl_rpm,
                "effizienzklasse": v.effizienzklasse or "–",
                "schutzart": v.schutzart or "–",
                "raum": v.raum or "–",
                "bezeichnung": v.bezeichnung or "–",
                "notizen": v.notizen or "",
                "fotos": fotos,
                "ki_vertrauen": v.ki_vertrauen or 0,
            })

        # Filter-Optionen
        alle_typen = (
            session.query(Verbraucher.geraetetyp)
            .filter_by(standort_id=standort_id)
            .distinct().all()
        )
        alle_hersteller = (
            session.query(Verbraucher.hersteller)
            .filter_by(standort_id=standort_id)
            .distinct().all()
        )

        berichte = (
            session.query(Bericht)
            .filter_by(standort_id=standort_id)
            .order_by(Bericht.erstellt_am.desc())
            .all()
        )
        berichte_daten = [
            {
                "id": b.id,
                "titel": b.titel or "Report",
                "erstellt_am": b.erstellt_am.strftime("%d.%m.%Y %H:%M") if b.erstellt_am else "",
                "anzahl": b.anzahl_verbraucher or 0,
                "hat_pdf": bool(b.pdf_pfad and os.path.exists(b.pdf_pfad)),
            }
            for b in berichte
        ]

    return templates.TemplateResponse("standort.html", {
        "request": request,
        "standort": standort_info,
        "verbraucher": verbraucher_daten,
        "gesamt_kw": gesamt_kw,
        "berichte": berichte_daten,
        "verfuegbare_typen": [t[0] for t in alle_typen if t[0]],
        "verfuegbare_hersteller": [h[0] for h in alle_hersteller if h[0]],
        "filter_typ": typ or "",
        "filter_hersteller": hersteller or "",
        "filter_effizienz": effizienz or "",
    })


@app.get("/foto/{foto_id}")
async def foto_anzeigen(foto_id: int, auth=Depends(auth_pruefen)):
    """Foto anzeigen."""
    with get_session() as session:
        foto = session.get(TypschildFoto, foto_id)
        if not foto:
            return HTMLResponse("<h1>Foto nicht gefunden</h1>", status_code=404)
        dateipfad = foto.dateipfad

    abs_pfad = os.path.abspath(dateipfad)
    if not os.path.exists(abs_pfad):
        return HTMLResponse("<h1>Fotodatei nicht gefunden</h1>", status_code=404)

    return FileResponse(abs_pfad, media_type="image/jpeg")


@app.get("/bericht/{bericht_id}/download")
async def bericht_download(bericht_id: int, auth=Depends(auth_pruefen)):
    """PDF-Report herunterladen."""
    with get_session() as session:
        bericht = session.get(Bericht, bericht_id)
        if not bericht or not bericht.pdf_pfad:
            return HTMLResponse("<h1>Bericht nicht gefunden</h1>", status_code=404)
        pdf_pfad = bericht.pdf_pfad

    if not os.path.exists(pdf_pfad):
        return HTMLResponse("<h1>PDF-Datei nicht gefunden</h1>", status_code=404)

    return FileResponse(
        pdf_pfad,
        media_type="application/pdf",
        filename=os.path.basename(pdf_pfad),
    )


@app.get("/export/{standort_id}/csv")
async def export_csv(standort_id: int, auth=Depends(auth_pruefen)):
    """Exportiert Verbraucher als CSV."""
    with get_session() as session:
        standort = session.get(Standort, standort_id)
        if not standort:
            return HTMLResponse("<h1>Standort nicht gefunden</h1>", status_code=404)
        standort_name = standort.name

        verbraucher = (
            session.query(Verbraucher)
            .filter_by(standort_id=standort_id)
            .order_by(Verbraucher.geraetetyp)
            .all()
        )

        rows = []
        for v in verbraucher:
            rows.append({
                "ID": v.id,
                "Gerätetyp": v.geraetetyp or "",
                "Hersteller": v.hersteller or "",
                "Modell": v.modell or "",
                "Seriennummer": v.seriennummer or "",
                "Baujahr": v.baujahr or "",
                "Leistung_kW": v.leistung_kw or "",
                "Spannung_V": v.spannung_v or "",
                "Strom_A": v.strom_a or "",
                "Effizienzklasse": v.effizienzklasse or "",
                "Schutzart": v.schutzart or "",
                "Raum": v.raum or "",
                "Bezeichnung": v.bezeichnung or "",
            })

    output = io.StringIO()
    if rows:
        writer = csv.DictWriter(output, fieldnames=rows[0].keys(), delimiter=";")
        writer.writeheader()
        writer.writerows(rows)

    safe_name = standort_name.replace(" ", "_")
    filename = f"Verbraucher_{safe_name}_{date.today().strftime('%Y-%m-%d')}.csv"

    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8-sig")),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/api/stats/{standort_id}")
async def api_stats(standort_id: int, auth=Depends(auth_pruefen)):
    """JSON-API: Statistiken für einen Standort."""
    with get_session() as session:
        gesamt = session.query(Verbraucher).filter_by(standort_id=standort_id).count()
        gesamt_kw = (
            session.query(func.sum(Verbraucher.leistung_kw))
            .filter_by(standort_id=standort_id)
            .scalar()
        ) or 0

        fotos = (
            session.query(TypschildFoto).join(Verbraucher)
            .filter(Verbraucher.standort_id == standort_id).count()
        )

        # Gerätetyp-Verteilung
        typ_counts = (
            session.query(Verbraucher.geraetetyp, func.count())
            .filter_by(standort_id=standort_id)
            .group_by(Verbraucher.geraetetyp)
            .all()
        )

        # Effizienzklassen-Verteilung
        eff_counts = (
            session.query(Verbraucher.effizienzklasse, func.count())
            .filter_by(standort_id=standort_id)
            .group_by(Verbraucher.effizienzklasse)
            .all()
        )

    return {
        "gesamt_verbraucher": gesamt,
        "gesamt_kw": round(gesamt_kw, 1),
        "fotos": fotos,
        "geraetetypen": {t or "Sonstiges": c for t, c in typ_counts},
        "effizienzklassen": {e or "–": c for e, c in eff_counts},
    }
