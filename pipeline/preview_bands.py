"""Genera una imagen de control con B8A y B12 (antes/después) para verificar
a simple vista la máscara de nubes/sombra/agua antes de calcular NBR."""

import copy
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from pystac_client import Client

from config import DATE_RANGE_AFTER, DATE_RANGE_BEFORE
from load_bands import load_clean_bands
from search_scenes import CATALOG_URL, best_scene

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "bands_preview.png"


def plot_bands(
    b8a_before: xr.DataArray,
    b8a_after: xr.DataArray,
    b12_before: xr.DataArray,
    b12_after: xr.DataArray,
    output_path: Path = OUTPUT_PATH,
) -> Path:
    """Grafica las 4 bandas en escala de grises, con los NaN (zonas tapadas) en rojo."""
    cmap = copy.copy(plt.cm.gray)
    cmap.set_bad(color="red")

    panels = [
        ("B8A - Antes", b8a_before),
        ("B8A - Después", b8a_after),
        ("B12 - Antes", b12_before),
        ("B12 - Después", b12_after),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(11, 10))
    for ax, (title, band) in zip(axes.flat, panels):
        data = band.values
        vmin, vmax = np.nanpercentile(data, [2, 98])
        ax.imshow(data, cmap=cmap, vmin=vmin, vmax=vmax)
        ax.set_title(title)
        ax.axis("off")

    fig.suptitle(
        "Incendio Tenerife, agosto 2023 — bandas crudas "
        "(en rojo: nube/sombra/agua tapada)",
        fontsize=12,
    )
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=120)
    return output_path


def main() -> None:
    """Carga las bandas de las dos escenas y guarda la imagen de control."""
    catalog = Client.open(CATALOG_URL)
    before_item = best_scene(catalog, DATE_RANGE_BEFORE)
    after_item = best_scene(catalog, DATE_RANGE_AFTER)

    b8a_before, b12_before = load_clean_bands(before_item)
    b8a_after, b12_after = load_clean_bands(after_item)

    output_path = plot_bands(b8a_before, b8a_after, b12_before, b12_after)
    print(f"Guardado en {output_path}")


if __name__ == "__main__":
    main()
