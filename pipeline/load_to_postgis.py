"""Carga los polígonos de severidad (del #6) a la base PostGIS levantada con
docker-compose.yml."""

from pathlib import Path

import geopandas as gpd
from sqlalchemy import create_engine

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "severity.geojson"
DB_URL = "postgresql+psycopg2://canarias:canarias@localhost:5432/canarias_burn_severity"
TABLE_NAME = "severity_polygons"


def main() -> None:
    """Lee severity.geojson, calcula hectáreas en la proyección métrica original
    (antes de reproyectar, porque en grados no tiene sentido), reproyecta a
    EPSG:4326 (la que espera un visor web tipo Leaflet) y reemplaza la tabla."""
    gdf = gpd.read_file(DATA_PATH)
    gdf["area_ha"] = gdf.geometry.area / 10_000
    gdf = gdf.to_crs(epsg=4326)

    engine = create_engine(DB_URL)
    gdf.to_postgis(TABLE_NAME, engine, if_exists="replace", index=True, index_label="id")

    print(f"{len(gdf)} polígonos cargados en la tabla '{TABLE_NAME}'.")


if __name__ == "__main__":
    main()
