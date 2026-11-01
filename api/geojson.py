"""Transforma filas de la base en GeoJSON / JSON para la API. Son funciones
puras (sin tocar la base) para poder testearlas sin una base PostGIS real."""

import json
from typing import Mapping, Sequence


def build_feature(row: Mapping) -> dict:
    """Convierte una fila (id, class_id, severity, area_ha, geojson) en un
    Feature GeoJSON, con la geometría ya parseada (viene como texto de
    ST_AsGeoJSON)."""
    return {
        "type": "Feature",
        "id": row["id"],
        "geometry": json.loads(row["geojson"]),
        "properties": {
            "class_id": row["class_id"],
            "severity": row["severity"],
            "area_ha": row["area_ha"],
        },
    }


def build_feature_collection(rows: Sequence[Mapping]) -> dict:
    """Envuelve varias filas en un FeatureCollection GeoJSON."""
    return {
        "type": "FeatureCollection",
        "features": [build_feature(row) for row in rows],
    }


def build_stats(rows: Sequence[Mapping]) -> list[dict]:
    """Convierte las filas agregadas por clase en una lista lista para JSON,
    redondeando las hectáreas a 2 decimales."""
    return [
        {
            "class_id": row["class_id"],
            "severity": row["severity"],
            "polygon_count": row["polygon_count"],
            "area_ha": round(row["area_ha"], 2),
        }
        for row in rows
    ]
