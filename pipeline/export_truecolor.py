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
from load_bands import EPSG
from search_scenes import CATALOG_URL, best_scene

RGB_BANDS = ["B04", "B03", "B02"]
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Sombra de nube, nube media/alta probabilidad, cirros: no se usan para
# ocultar píxeles (eso fue el bug del agua y de las nubes negras — ver el
# historial de este archivo), sino solo para EXCLUIRLOS del cálculo del
# estiramiento de contraste en to_rgba(). Una nube es mucho más brillante
# que cualquier terreno real; si entra en la cuenta del percentil 98, corre
# el "blanco de referencia" tan arriba que todo el paisaje normal queda
# aplastado y oscuro.
CLOUD_LIKE = [3, 8, 9, 10]


def load_true_color(item: Item) -> tuple[xr.DataArray, xr.DataArray]:
    """Carga B04/B03/B02 (rojo/verde/azul) y la máscara de nube/sombra/cirros
    (ver CLOUD_LIKE), recortadas al bbox. Ningún píxel se oculta en la
    imagen final — la máscara solo se usa para las estadísticas de
    contraste en to_rgba()."""
    signed_item = planetary_computer.sign(item)
    stack = stackstac.stack(
        [signed_item],
        assets=RGB_BANDS + ["SCL"],
        bounds_latlon=BBOX,
        epsg=EPSG,
        resolution=20,
    ).squeeze("time")
    rgb = stack.sel(band=RGB_BANDS)
    is_cloud_like = stack.sel(band="SCL").isin(CLOUD_LIKE)
    return rgb, is_cloud_like


def to_rgba(rgb: xr.DataArray, is_cloud_like: xr.DataArray) -> np.ndarray:
    """Convierte las 3 bandas crudas a una imagen RGBA 0-1. El estiramiento
    de contraste (percentiles 2-98) se calcula solo con los píxeles que no
    son nube/sombra/cirros, pero se aplica a TODOS — una nube de verdad
    termina saturada en blanco puro, que es como se ve en la realidad."""
    data = rgb.values  # (3, alto, ancho), orden R,G,B
    clear = ~is_cloud_like.values  # (alto, ancho)
    stretched = np.empty_like(data, dtype="float64")
    for i in range(3):
        band = data[i]
        low, high = np.nanpercentile(band[clear], [2, 98])
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
        rgba = to_rgba(*load_true_color(item))
        output_path = DATA_DIR / filename
        plt.imsave(output_path, rgba, origin="upper")
        print(f"{label}: guardado en {output_path}")


if __name__ == "__main__":
    main()
