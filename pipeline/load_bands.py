"""Carga B8A, B12 y SCL de las escenas elegidas, recorta al área y enmascara
nubes, sombras y agua usando la clasificación de la propia banda SCL."""

import planetary_computer
import stackstac
import xarray as xr
from pystac import Item
from pystac_client import Client

from config import BBOX, DATE_RANGE_AFTER, DATE_RANGE_BEFORE
from search_scenes import CATALOG_URL, best_scene

BANDS = ["B8A", "B12", "SCL"]
EPSG = 32628  # UTM 28N: la zona de la escena (tile T28RCS cubre Tenerife)

# Clases de la banda SCL (Scene Classification) que tapamos antes de calcular
# NBR: sombra de nube, agua, nube (media/alta probabilidad) y cirros delgados.
SCL_CLOUD_SHADOW_WATER = [3, 6, 8, 9, 10]


def load_clean_bands(item: Item) -> tuple[xr.DataArray, xr.DataArray]:
    """Carga B8A/B12 de un item, recortadas al bbox, con nubes/sombras/agua en NaN."""
    signed_item = planetary_computer.sign(item)
    stack = stackstac.stack(
        [signed_item],
        assets=BANDS,
        bounds_latlon=BBOX,
        epsg=EPSG,
        resolution=20,
    ).squeeze("time")

    scl = stack.sel(band="SCL")
    is_dirty = scl.isin(SCL_CLOUD_SHADOW_WATER)

    b8a = stack.sel(band="B8A").where(~is_dirty)
    b12 = stack.sel(band="B12").where(~is_dirty)
    return b8a, b12


def main() -> None:
    """Carga las bandas de las dos escenas y muestra cuánta área quedó sin nubes."""
    catalog = Client.open(CATALOG_URL)

    before_item = best_scene(catalog, DATE_RANGE_BEFORE)
    after_item = best_scene(catalog, DATE_RANGE_AFTER)

    b8a_before, _ = load_clean_bands(before_item)
    b8a_after, _ = load_clean_bands(after_item)

    for label, b8a in [("Antes", b8a_before), ("Después", b8a_after)]:
        total = b8a.size
        valid = int(b8a.notnull().sum())
        print(
            f"{label}: {b8a.shape[0]}x{b8a.shape[1]} píxeles, "
            f"{valid}/{total} válidos ({valid / total:.1%} sin nubes/sombra/agua)"
        )


if __name__ == "__main__":
    main()
