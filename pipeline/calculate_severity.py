"""Calcula NBR antes/después, dNBR, y clasifica la severidad del incendio
según los umbrales USGS (Key & Benson)."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import xarray as xr
from pystac_client import Client

from config import DATE_RANGE_AFTER, DATE_RANGE_BEFORE, SEVERITY_THRESHOLDS
from load_bands import load_clean_bands
from search_scenes import CATALOG_URL, best_scene

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "severity_map.png"

SEVERITY_COLORS = [
    "#1a9641",  # Rebrote alto
    "#a6d96a",  # Rebrote bajo
    "#f7f7b0",  # No quemado
    "#fee08b",  # Severidad baja
    "#fdae61",  # Severidad moderada-baja
    "#f46d43",  # Severidad moderada-alta
    "#a50026",  # Severidad alta
]


def compute_nbr(b8a: xr.DataArray, b12: xr.DataArray) -> xr.DataArray:
    """Calcula el NBR = (B8A - B12) / (B8A + B12) píxel por píxel."""
    return (b8a - b12) / (b8a + b12)


def classify_severity(dnbr: xr.DataArray) -> xr.DataArray:
    """Asigna a cada píxel el índice de su clase de severidad (NaN = sin dato)."""
    classes = xr.full_like(dnbr, -1)
    for i, (_, low, high) in enumerate(SEVERITY_THRESHOLDS):
        in_range = (dnbr >= low) & (dnbr < high)
        classes = classes.where(~in_range, i)
    classes = classes.where(dnbr.notnull())

    valid = int(dnbr.notnull().sum())
    classified = int(classes.isin(range(len(SEVERITY_THRESHOLDS))).sum())
    assert classified == valid, (
        f"{valid - classified} píxeles válidos quedaron sin clase: "
        "revisar que SEVERITY_THRESHOLDS cubra todo el rango sin huecos"
    )
    return classes


def plot_severity(severity: xr.DataArray, output_path: Path = OUTPUT_PATH) -> Path:
    """Dibuja el raster de severidad con la paleta de colores y lo guarda en un PNG."""
    n_classes = len(SEVERITY_THRESHOLDS)
    cmap = mcolors.ListedColormap(SEVERITY_COLORS)
    cmap.set_bad(color="lightgray")

    fig, ax = plt.subplots(figsize=(9, 8))
    im = ax.imshow(severity.values, cmap=cmap, vmin=-0.5, vmax=n_classes - 0.5)
    ax.set_title("Severidad del incendio — Tenerife, agosto 2023 (dNBR clasificado)")
    ax.axis("off")

    cbar = fig.colorbar(im, ax=ax, ticks=range(n_classes))
    cbar.ax.set_yticklabels([label for label, _, _ in SEVERITY_THRESHOLDS])

    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=120)
    return output_path


def main() -> None:
    """Calcula dNBR para las dos escenas, clasifica la severidad y grafica el resultado."""
    catalog = Client.open(CATALOG_URL)
    before_item = best_scene(catalog, DATE_RANGE_BEFORE)
    after_item = best_scene(catalog, DATE_RANGE_AFTER)

    b8a_before, b12_before = load_clean_bands(before_item)
    b8a_after, b12_after = load_clean_bands(after_item)

    nbr_before = compute_nbr(b8a_before, b12_before)
    nbr_after = compute_nbr(b8a_after, b12_after)
    dnbr = nbr_before - nbr_after

    severity = classify_severity(dnbr)

    valid = int(dnbr.notnull().sum())
    print(f"Píxeles válidos (dato en ambas fechas): {valid}/{dnbr.size} "
          f"({valid / dnbr.size:.1%})\n")
    for i, (label, low, high) in enumerate(SEVERITY_THRESHOLDS):
        count = int((severity == i).sum())
        pct = count / valid if valid else 0
        print(f"  {label:25s} [{low:+.3f}, {high:+.3f}): {count:7d} px ({pct:.1%})")

    output_path = plot_severity(severity)
    print(f"\nGuardado en {output_path}")


if __name__ == "__main__":
    main()
