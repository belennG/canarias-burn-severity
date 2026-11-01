"""API con FastAPI que sirve los polígonos de severidad (issue #9), para
que el visor React + Leaflet (issue #10) los consuma como GeoJSON."""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from database import fetch_severity_rows, fetch_stats_rows
from geojson import build_feature_collection, build_stats

app = FastAPI(title="Canarias Burn Severity API")

# Orígenes del servidor de desarrollo de Vite (issue #10). El frontend
# desplegado en Netlify (issue #12) usa datos estáticos, no esta API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/severity")
def get_severity(severity: str | None = Query(default=None)) -> dict:
    """Polígonos de severidad como GeoJSON. `severity` filtra por clase
    (por ejemplo "Severidad alta"); sin filtro, devuelve los 12.982."""
    rows = fetch_severity_rows(severity=severity)
    return build_feature_collection(rows)


@app.get("/severity/stats")
def get_severity_stats() -> list[dict]:
    """Hectáreas y cantidad de polígonos por clase, en orden de class_id."""
    rows = fetch_stats_rows()
    return build_stats(rows)
