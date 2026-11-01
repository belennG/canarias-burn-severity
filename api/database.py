"""Acceso a la tabla severity_polygons (cargada por pipeline/load_to_postgis.py,
issue #8) en la base PostGIS levantada con docker-compose.yml."""

import os

from sqlalchemy import create_engine, text

DB_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg2://canarias:canarias@localhost:5432/canarias_burn_severity",
)
TABLE_NAME = "severity_polygons"

engine = create_engine(DB_URL)

SEVERITY_QUERY = (
    f"SELECT id, class_id, severity, area_ha, ST_AsGeoJSON(geometry) AS geojson "
    f"FROM {TABLE_NAME}"
)

STATS_QUERY = text(
    f"SELECT class_id, severity, COUNT(*) AS polygon_count, SUM(area_ha) AS area_ha "
    f"FROM {TABLE_NAME} GROUP BY class_id, severity ORDER BY class_id"
)


def fetch_severity_rows(severity: str | None = None):
    """Devuelve las filas de severity_polygons, opcionalmente filtradas por clase."""
    query = SEVERITY_QUERY
    params = {}
    if severity is not None:
        query += " WHERE severity = :severity"
        params["severity"] = severity
    query += " ORDER BY id"

    with engine.connect() as conn:
        return conn.execute(text(query), params).mappings().all()


def fetch_stats_rows():
    """Devuelve hectáreas y cantidad de polígonos por clase de severidad."""
    with engine.connect() as conn:
        return conn.execute(STATS_QUERY).mappings().all()
