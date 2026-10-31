"""Busca las escenas Sentinel-2 L2A con menos nubes para las ventanas antes/después."""

from pystac import Item
from pystac_client import Client

from config import (
    BBOX,
    DATE_RANGE_AFTER,
    DATE_RANGE_BEFORE,
    MAX_CLOUD_COVER,
    STAC_COLLECTION,
)

CATALOG_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"


def best_scene(catalog: Client, date_range: tuple[str, str]) -> Item:
    """Busca escenas en una ventana de fechas y devuelve la de menos nubes."""
    start, end = date_range
    search = catalog.search(
        collections=[STAC_COLLECTION],
        bbox=BBOX,
        datetime=f"{start}/{end}",
        query={"eo:cloud_cover": {"lt": MAX_CLOUD_COVER}},
    )
    items = list(search.items())
    if not items:
        raise RuntimeError(
            f"No se encontraron escenas entre {start} y {end} "
            f"con menos de {MAX_CLOUD_COVER}% de nubes"
        )
    return min(items, key=lambda item: item.properties["eo:cloud_cover"])


def main() -> None:
    """Busca la mejor escena de cada ventana (antes/después) y la muestra por consola."""
    catalog = Client.open(CATALOG_URL)

    collection = catalog.get_collection(STAC_COLLECTION)
    print(f"Colección: {collection.id} ({collection.title})\n")

    before = best_scene(catalog, DATE_RANGE_BEFORE)
    after = best_scene(catalog, DATE_RANGE_AFTER)

    for label, item in [("Antes", before), ("Después", after)]:
        print(f"{label}: {item.id}")
        print(f"  Fecha: {item.properties['datetime']}")
        print(f"  Nubes: {item.properties['eo:cloud_cover']}%\n")


if __name__ == "__main__":
    main()
