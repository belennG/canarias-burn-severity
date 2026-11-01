"""Configuración del área de estudio y fechas para el incendio de Tenerife (agosto 2023)."""

# Bounding box [min_lon, min_lat, max_lon, max_lat] (WGS84 / EPSG:4326).
# Cubre los municipios afectados (Arafo, Candelaria, Güímar, El Rosario,
# La Orotava, Santa Úrsula, La Victoria, Fasnia, Arico, Vilaflor, Granadilla)
# y el Parque Nacional del Teide / Parque Natural Corona Forestal.
#
# Es una caja aproximada a partir de los municipios afectados reportados por
# Protección Civil (Gobierno de Canarias). El perímetro oficial está en el
# producto "Grading" de la activación Copernicus EMS EMSR685 (AOI 01
# Candelaria, imagen del 26/08/2023), usado como referencia en la validación
# (issue #7).
# https://mapping.emergency.copernicus.eu/activations/EMSR685/download
#
# El borde norte (28.40) se corrigió en el issue #7: el perímetro oficial
# llega hasta latitud ~28.4546, así que la caja original dejaba ~23% del
# incendio real (2.864 ha) fuera de la zona descargada/procesada. 28.60 le da
# el mismo margen que ya tenían los otros tres bordes.
BBOX = [-16.75, 28.10, -16.25, 28.60]

# Ventanas de búsqueda de escenas Sentinel-2 L2A.
# El incendio empezó la noche del 15/08/2023 y quedó estabilizado hacia
# el 26/08/2023. Se deja margen a cada lado para poder elegir la escena
# con menos nubes dentro de cada ventana.
DATE_RANGE_BEFORE = ("2023-07-25", "2023-08-14")
DATE_RANGE_AFTER = ("2023-09-01", "2023-09-30")

# Superficie oficial reportada (Ministerio del Interior, 24/08/2023) para
# comparar con el área total calculada a partir del raster de severidad
# (issue #7). Fuentes varían entre ~14.751 y ~14.878 ha.
REPORTED_AREA_HA = 14_751

# ID de la colección en el catálogo STAC de Planetary Computer. Por ahora es el
# nombre estándar conocido de Sentinel-2 L2A; se confirma en el issue #3
# listando las colecciones disponibles con pystac_client antes de buscar.
STAC_COLLECTION = "sentinel-2-l2a"

# Umbral de nubosidad (%) para descartar escenas. Es un valor de partida
# razonable (20% es exigente pero no tanto como para no encontrar escenas en
# una ventana de ~3-4 semanas); se ajusta en el issue #3 según lo que
# devuelva realmente la búsqueda para esta área y estas fechas.
MAX_CLOUD_COVER = 20

# Clases de severidad por dNBR, según los umbrales USGS (Key & Benson, FIREMON),
# expresados en la escala nativa de NBR [-1, 1] en vez del entero x1000 original
# de la publicación. Cada tupla es (nombre, mínimo incluido, máximo excluido).
# Los límites son contiguos a propósito (el máximo de una clase es el mínimo
# de la siguiente) para que ningún valor de dNBR quede sin clasificar.
SEVERITY_THRESHOLDS = [
    ("Rebrote alto", -2.000, -0.250),
    ("Rebrote bajo", -0.250, -0.100),
    ("No quemado", -0.100, 0.100),
    ("Severidad baja", 0.100, 0.270),
    ("Severidad moderada-baja", 0.270, 0.440),
    ("Severidad moderada-alta", 0.440, 0.660),
    ("Severidad alta", 0.660, 2.000),
]
