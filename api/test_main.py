"""Tests de las transformaciones a GeoJSON/JSON y del healthcheck: no tocan
la base real, solo filas de juguete, para poder correr sin Docker levantado."""

from fastapi.testclient import TestClient

from geojson import build_feature, build_feature_collection, build_stats
from main import app

client = TestClient(app)

FILA_DE_JUGUETE = {
    "id": 5183,
    "class_id": 6,
    "severity": "Severidad alta",
    "area_ha": 0.04,
    "geojson": '{"type": "Polygon", "coordinates": [[[0, 0], [0, 1], [1, 1], [0, 0]]]}',
}


def test_build_feature_parsea_la_geometria_y_arma_las_properties():
    """build_feature debe devolver un Feature válido, con la geometría ya
    parseada (no como el texto crudo que devuelve ST_AsGeoJSON)."""
    feature = build_feature(FILA_DE_JUGUETE)
    assert feature["type"] == "Feature"
    assert feature["id"] == 5183
    assert feature["geometry"] == {
        "type": "Polygon",
        "coordinates": [[[0, 0], [0, 1], [1, 1], [0, 0]]],
    }
    assert feature["properties"] == {
        "class_id": 6,
        "severity": "Severidad alta",
        "area_ha": 0.04,
    }


def test_build_feature_collection_envuelve_varias_filas():
    collection = build_feature_collection([FILA_DE_JUGUETE, FILA_DE_JUGUETE])
    assert collection["type"] == "FeatureCollection"
    assert len(collection["features"]) == 2


def test_build_stats_redondea_las_hectareas():
    """Regresión: SUM(area_ha) en Postgres puede devolver muchos decimales;
    la API debe redondear a 2 antes de exponerlo."""
    fila = {"class_id": 2, "severity": "No quemado", "polygon_count": 500, "area_ha": 94911.321789}
    stats = build_stats([fila])
    assert stats == [
        {"class_id": 2, "severity": "No quemado", "polygon_count": 500, "area_ha": 94911.32}
    ]


def test_health_responde_ok_sin_tocar_la_base():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
