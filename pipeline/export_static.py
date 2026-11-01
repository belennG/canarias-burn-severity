"""Saca una foto de la API (GeoJSON, estadísticas e imágenes) y la deja en
web/public/, lista para el build de producción (Netlify, issue #12), que no
tiene ninguna API ni base de datos corriendo — necesita `uvicorn` activo en
:8000.

El GeoJSON se simplifica y las imágenes se recomprimen a JPEG: son archivos
que quedan commiteados al repo y Netlify los sirve tal cual, así que acá el
tamaño importa de una forma en la que no importa en la API local."""

import json
from pathlib import Path

import httpx
import shapely
from PIL import Image
from shapely.geometry import mapping, shape

API_URL = "http://localhost:8000"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
WEB_PUBLIC = Path(__file__).resolve().parent.parent / "web" / "public"

# ~22m a esta latitud, un píxel de 20m: no deforma la forma a simple vista
# (el borde ya es una escalera de píxeles, no una curva suave), pero achica
# el GeoJSON de 13 a 7 MB.
SIMPLIFY_TOLERANCE = 0.0002


def simplify_geojson(raw: bytes) -> bytes:
    """Simplifica cada geometría (Douglas-Peucker + snapping a una grilla) y
    reserializa sin espacios, para achicar el archivo."""
    collection = json.loads(raw)
    for feature in collection["features"]:
        geom = shape(feature["geometry"])
        geom = geom.simplify(SIMPLIFY_TOLERANCE, preserve_topology=True)
        geom = shapely.set_precision(geom, grid_size=0.00001)
        feature["geometry"] = mapping(geom)
    return json.dumps(collection, separators=(",", ":")).encode()


def to_jpeg(png_path: Path, jpeg_path: Path, quality: int = 85) -> None:
    """Convierte el PNG (con alpha donde hay nubes/agua tapadas) a JPEG sobre
    fondo negro: JPEG no tiene canal alfa, pero pesa una fracción del PNG."""
    with Image.open(png_path) as img:
        background = Image.new("RGB", img.size, (0, 0, 0))
        background.paste(img, mask=img.split()[3])
        background.save(jpeg_path, "JPEG", quality=quality)


def main() -> None:
    (WEB_PUBLIC / "imagery").mkdir(parents=True, exist_ok=True)

    severity = httpx.get(f"{API_URL}/severity", timeout=30)
    severity.raise_for_status()
    simplified = simplify_geojson(severity.content)
    (WEB_PUBLIC / "severity.geojson").write_bytes(simplified)
    print(f"/severity -> severity.geojson ({len(severity.content):,} -> {len(simplified):,} bytes)")

    stats = httpx.get(f"{API_URL}/severity/stats", timeout=30)
    stats.raise_for_status()
    (WEB_PUBLIC / "stats.json").write_bytes(stats.content)
    print(f"/severity/stats -> stats.json ({len(stats.content):,} bytes)")

    for filename in ["rgb_before", "rgb_after"]:
        src = DATA_DIR / f"{filename}.png"
        dst = WEB_PUBLIC / "imagery" / f"{filename}.jpg"
        to_jpeg(src, dst)
        print(f"{src} ({src.stat().st_size:,} bytes) -> {dst} ({dst.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
