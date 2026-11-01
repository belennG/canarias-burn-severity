"""Genera imágenes RGB (color verdadero) de antes/después del incendio, para
el comparador del visor (issue #11)."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import planetary_computer
import stackstac
import xarray as xr
from pystac import Item
from pystac_client import Client

from config import BBOX, DATE_RANGE_AFTER, DATE_RANGE_BEFORE
from load_bands import EPSG, SCL_CLOUD_SHADOW_WATER
from search_scenes import CATALOG_URL, best_scene

RGB_BANDS = ["B04", "B03", "B02"]
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_true_color(item: Item) -> xr.DataArray:
    """Carga B04/B03/B02 (rojo/verde/azul), recortadas al bbox, con nubes/
    sombras/agua en NaN (misma máscara SCL que load_bands.load_clean_bands)."""
    signed_item = planetary_computer.sign(item)
    stack = stackstac.stack(
        [signed_item],
        assets=RGB_BANDS + ["SCL"],
        bounds_latlon=BBOX,
        epsg=EPSG,
        resolution=20,
    ).squeeze("time")

    scl = stack.sel(band="SCL")
    is_dirty = scl.isin(SCL_CLOUD_SHADOW_WATER)
    return stack.sel(band=RGB_BANDS).where(~is_dirty)


def to_rgba(rgb: xr.DataArray) -> np.ndarray:
    """Convierte las 3 bandas crudas a una imagen RGBA 0-1: estiramiento de
    contraste por banda (percentiles 2-98) y alpha=0 donde no hay dato."""
    data = rgb.values  # (3, alto, ancho), orden R,G,B
    stretched = np.empty_like(data, dtype="float64")
    for i in range(3):
        band = data[i]
        low, high = np.nanpercentile(band, [2, 98])
        stretched[i] = np.clip((band - low) / (high - low), 0, 1)

    alpha = np.where(np.isnan(data).any(axis=0), 0.0, 1.0)
    rgba = np.concatenate([np.nan_to_num(stretched), alpha[None]], axis=0)
    return np.transpose(rgba, (1, 2, 0))  # (alto, ancho, 4), lo que pide imsave


def main() -> None:
    """Genera y guarda data/rgb_before.png y data/rgb_after.png."""
    catalog = Client.open(CATALOG_URL)
    before_item = best_scene(catalog, DATE_RANGE_BEFORE)
    after_item = best_scene(catalog, DATE_RANGE_AFTER)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for label, item, filename in [
        ("Antes", before_item, "rgb_before.png"),
        ("Después", after_item, "rgb_after.png"),
    ]:
        rgba = to_rgba(load_true_color(item))
        output_path = DATA_DIR / filename
        plt.imsave(output_path, rgba, origin="upper")
        print(f"{label}: guardado en {output_path}")


if __name__ == "__main__":
    main()
