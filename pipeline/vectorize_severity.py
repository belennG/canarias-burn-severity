"""Convierte el raster de severidad en polígonos y calcula hectáreas por clase."""

from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio.features
import xarray as xr
from pystac_client import Client
from shapely.geometry import shape as shapely_shape

from calculate_severity import SEVERITY_COLORS, classify_severity, compute_nbr
from config import DATE_RANGE_AFTER, DATE_RANGE_BEFORE, SEVERITY_THRESHOLDS
from load_bands import EPSG, load_clean_bands
from search_scenes import CATALOG_URL, best_scene

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "severity.geojson"
PLOT_PATH = Path(__file__).resolve().parent.parent / "data" / "severity_vectors.png"

CLASS_LABELS = [label for label, _, _ in SEVERITY_THRESHOLDS]
PIXEL_AREA_HA = (20 * 20) / 10_000  # resolución 20m -> 400 m² -> 0.04 ha


def vectorize(severity: xr.DataArray) -> gpd.GeoDataFrame:
    """Convierte cada región contigua de píxeles con la misma clase en un polígono.

    Usa severity.attrs["transform"] (el que viene de stackstac, referido al borde
    de cada píxel) y no severity.rio.transform() (que rioxarray calcula asumiendo
    que las coordenadas son el centro del píxel, y queda desalineado medio píxel).
    """
    data = severity.values
    mask = ~np.isnan(data)
    data_int = np.where(mask, data, 0).astype("int32")
    transform = severity.attrs["transform"]

    shapes = rasterio.features.shapes(data_int, mask=mask, transform=transform)
    records = [
        {
            "class_id": int(value),
            "severity": CLASS_LABELS[int(value)],
            "geometry": shapely_shape(geom),
        }
        for geom, value in shapes
    ]
    return gpd.GeoDataFrame(records, crs=f"EPSG:{EPSG}")


def summarize_area(gdf: gpd.GeoDataFrame) -> pd.Series:
    """Suma el área (ha) de cada clase de severidad, en el orden de SEVERITY_THRESHOLDS."""
    areas = gdf.geometry.area / 10_000
    return areas.groupby(gdf["severity"]).sum().reindex(CLASS_LABELS, fill_value=0.0)


def plot_vectors(gdf: gpd.GeoDataFrame, output_path: Path = PLOT_PATH) -> Path:
    """Dibuja los polígonos de severidad (mismos colores que el raster) y los guarda."""
    color_by_class = dict(zip(CLASS_LABELS, SEVERITY_COLORS))
    colors = gdf["severity"].map(color_by_class)

    fig, ax = plt.subplots(figsize=(9, 8))
    gdf.plot(color=colors, ax=ax, edgecolor="none")
    ax.set_title("Severidad del incendio — polígonos vectorizados")
    ax.axis("off")
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=120)
    return output_path


def main() -> None:
    """Vectoriza la severidad, calcula hectáreas por clase y las compara contra
    el conteo de píxeles (sanity check), y guarda el GeoJSON y un PNG de control."""
    catalog = Client.open(CATALOG_URL)
    before_item = best_scene(catalog, DATE_RANGE_BEFORE)
    after_item = best_scene(catalog, DATE_RANGE_AFTER)

    b8a_before, b12_before = load_clean_bands(before_item)
    b8a_after, b12_after = load_clean_bands(after_item)

    nbr_before = compute_nbr(b8a_before, b12_before)
    nbr_after = compute_nbr(b8a_after, b12_after)
    dnbr = nbr_before - nbr_after
    severity = classify_severity(dnbr)

    gdf = vectorize(severity)
    area_by_class = summarize_area(gdf)

    print(f"{len(gdf)} polígonos generados.\n")
    print(f"{'Clase':25s} {'ha (vectorizado)':>18s} {'ha (por conteo)':>16s} {'diff':>8s}")
    for i, label in enumerate(CLASS_LABELS):
        vector_ha = area_by_class[label]
        pixel_ha = int((severity == i).sum()) * PIXEL_AREA_HA
        print(f"{label:25s} {vector_ha:18.2f} {pixel_ha:16.2f} {vector_ha - pixel_ha:+8.4f}")

    gdf.to_file(OUTPUT_PATH, driver="GeoJSON")
    print(f"\nGuardado en {OUTPUT_PATH}")

    plot_path = plot_vectors(gdf)
    print(f"Guardado en {plot_path}")


if __name__ == "__main__":
    main()
