"""Compara el perímetro oficial de Copernicus EMS (EMSR685, producto Grading)
contra el área clasificada como quemada por nuestro pipeline: superposición
espacial (IoU), no solo una comparación de hectáreas totales."""

from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from shapely.ops import unary_union

from load_bands import EPSG

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OFFICIAL_PATH = (
    DATA_DIR / "emsr685_grading" / "EMSR685_AOI01_GRA_PRODUCT_observedEventA_v1.json"
)
DETECTED_PATH = DATA_DIR / "severity.geojson"
PLOT_PATH = DATA_DIR / "validation_overlay.png"

BURNED_CLASSES = [
    "Severidad baja",
    "Severidad moderada-baja",
    "Severidad moderada-alta",
    "Severidad alta",
]


def load_official_perimeter():
    """Carga los 53 polígonos oficiales de Copernicus EMS y los une en uno solo,
    reproyectados a la misma grilla métrica (EPSG:32628) que usa el pipeline."""
    gdf = gpd.read_file(OFFICIAL_PATH).to_crs(epsg=EPSG)
    return unary_union(gdf.geometry.buffer(0))


def load_detected_area(gdf: gpd.GeoDataFrame):
    """Une los polígonos de severidad >= baja en una sola geometría 'detectada'."""
    burned = gdf[gdf["severity"].isin(BURNED_CLASSES)]
    return unary_union(burned.geometry.buffer(0))


def load_valid_footprint(gdf: gpd.GeoDataFrame):
    """Une TODOS los polígonos (incluido 'No quemado'), sea cual sea su clase:
    es la huella de lo que realmente tiene dato en nuestro análisis (sin nubes/
    sombra/agua). Sirve para saber qué parte del perímetro oficial ni siquiera
    pudimos evaluar."""
    return unary_union(gdf.geometry.buffer(0))


def compute_metrics(official, detected, valid_footprint) -> dict:
    """IoU, cobertura (% del oficial que detectamos) y precisión (% de lo
    detectado que es real), más el % del oficial que cae en zona sin dato."""
    intersection = official.intersection(detected)
    union = official.union(detected)
    official_con_dato = official.intersection(valid_footprint)

    return {
        "area_oficial_ha": official.area / 10_000,
        "area_detectada_ha": detected.area / 10_000,
        "area_interseccion_ha": intersection.area / 10_000,
        "iou": intersection.area / union.area,
        "cobertura (interseccion/oficial)": intersection.area / official.area,
        "precision (interseccion/detectado)": intersection.area / detected.area,
        "% oficial con dato (sin nubes)": official_con_dato.area / official.area,
    }


def plot_overlay(official, detected, valid_footprint, output_path: Path = PLOT_PATH) -> Path:
    """Dibuja la huella con dato, el perímetro oficial y el área detectada
    superpuestos, para ver a simple vista dónde coinciden y dónde no."""
    fig, ax = plt.subplots(figsize=(9, 8))

    gpd.GeoSeries([valid_footprint]).plot(ax=ax, color="#e8e8e8", label="Con dato (sin nubes)")
    gpd.GeoSeries([detected]).plot(ax=ax, color="#f46d43", alpha=0.6, label="Detectado (pipeline)")
    gpd.GeoSeries([official]).plot(
        ax=ax, facecolor="none", edgecolor="#1a1a1a", linewidth=1.2, label="Oficial (Copernicus EMS)"
    )

    ax.set_title("Validación: perímetro oficial vs. detectado por el pipeline")
    ax.axis("off")
    ax.legend(loc="lower left")
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=120)
    return output_path


def main() -> None:
    """Carga ambos perímetros, calcula las métricas de superposición y
    guarda el mapa de comparación."""
    gdf = gpd.read_file(DETECTED_PATH)

    official = load_official_perimeter()
    detected = load_detected_area(gdf)
    valid_footprint = load_valid_footprint(gdf)

    metrics = compute_metrics(official, detected, valid_footprint)
    for key, value in metrics.items():
        if "ha" in key:
            print(f"{key:35s}: {value:10.2f} ha")
        else:
            print(f"{key:35s}: {value:10.2%}")

    plot_path = plot_overlay(official, detected, valid_footprint)
    print(f"\nGuardado en {plot_path}")


if __name__ == "__main__":
    main()
