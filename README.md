# canaries-burn-severity

Severidad del incendio de Tenerife (agosto 2023) a partir de imágenes Sentinel-2 de antes y
después del fuego. Proyecto para la entrevista con Telespazio Ibérica (Software Engineer
GIS/GeoAI, Fuerteventura).

> Este README se irá ampliando. La versión final (problema, método, diagrama, limitaciones,
> capturas) es el issue #13.

## Objetivo

Medir dónde y con qué intensidad se quemó la vegetación, usando el índice **NBR** (Normalized
Burn Ratio) antes y después del incendio, y mostrarlo en un visor web.

- `NBR = (NIR − SWIR2) / (NIR + SWIR2)` → en Sentinel-2: `(B8A − B12) / (B8A + B12)`
- `dNBR = NBR_antes − NBR_después` → cuanto más alto, más severa la quema
- Clases de severidad según los umbrales USGS (Key & Benson)

## Stack

- **Pipeline**: Python — `pystac-client`, `planetary-computer`, `stackstac`, `rioxarray`,
  `rasterio`, `geopandas`, `numpy`, `matplotlib`
- **Datos**: Sentinel-2 L2A desde [Microsoft Planetary Computer](https://planetarycomputer.microsoft.com/)
  (STAC, sin cuenta para buscar)
- **Backend**: PostgreSQL + PostGIS (Docker), API con FastAPI
- **Frontend**: React + Vite + Leaflet (`react-leaflet`)
- **Deploy**: frontend en Netlify con datos estáticos; API local con `docker compose`

## Estructura del repo

```
pipeline/   # scripts/notebooks de procesamiento
api/        # FastAPI
web/        # React + Leaflet
data/       # datos descargados e intermedios (fuera de git)
docs/       # diagrama, capturas
docker-compose.yml
README.md
```

## Área de estudio

Incendio de Tenerife, agosto 2023 (Arafo, Candelaria, valle de Güímar y norte), activación
Copernicus EMS [EMSR685](https://mapping.emergency.copernicus.eu/activations/EMSR685/). El
área, las ventanas de fechas y la superficie oficial de referencia están en
[`pipeline/config.py`](pipeline/config.py), no hardcodeadas en el código de procesamiento.

El `BBOX` se corrigió después del issue #7: la validación contra el perímetro oficial mostró
que el borde norte original (lat. 28.40) dejaba ~23% del incendio real (2.864 ha) fuera de la
zona descargada. Con el borde corregido (28.60) el pipeline (#3-#8) se volvió a correr
completo y la cobertura oficial pasó a 100% (antes 79.8%) y el IoU de 60.9% a 73.9%.

## Notas para más adelante (ver issue #13)

- **Margen del BBOX elegido a mano**: los 4 bordes de `BBOX` (`pipeline/config.py`) son números
  redondos en grados, elegidos a ojo. Más prolijo: bounds del perímetro oficial + buffer fijo en
  metros (ej. 2 km) en la proyección métrica, para que el margen sea una decisión explícita y
  reproducible.
- **Dos "oficial" distintos, sin aclarar**: el panel de stats del visor compara el área detectada
  contra `REPORTED_AREA_HA` (14.751 ha, cifra de prensa de Protección Civil), mientras que
  `validate.py` compara contra el polígono exacto de Copernicus EMS (12.273,95 ha) — son fuentes
  distintas que no coinciden entre sí, y hoy conviven sin que quede claro en la UI/README cuál es
  cuál. Por eso el visor muestra 72% y la validación 79% de cobertura: no es un error, son
  denominadores distintos, pero conviene aclararlo (en el panel, o al menos en el README final).

## Cómo correrlo

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Los scripts se corren desde `pipeline/`, en orden:

```bash
cd pipeline
python3 search_scenes.py       # busca las escenas con menos nubes (issue #3)
python3 load_bands.py          # carga B8A/B12 y aplica la máscara de nubes (issue #4)
python3 preview_bands.py       # guarda data/bands_preview.png, para verificar a simple vista
python3 calculate_severity.py  # calcula NBR, dNBR y clasifica severidad (issue #5)
python3 vectorize_severity.py  # vectoriza a polígonos y calcula hectáreas por clase (issue #6)
python3 validate.py            # compara contra el perímetro oficial de Copernicus EMS (issue #7)
python3 export_truecolor.py    # guarda data/rgb_before.png y rgb_after.png, color verdadero (issue #11)
```

(`export_static.py`, para el deploy, va después — necesita la API corriendo, ver más abajo.)

Base de datos (PostGIS, en Docker):

```bash
docker compose up -d
cd pipeline
python3 load_to_postgis.py  # carga severity.geojson a la tabla severity_polygons (issue #8)
```

API (FastAPI, issue #9) — necesita la base de datos corriendo:

```bash
cd api
uvicorn main:app --reload --port 8000
```

- `GET /health` — healthcheck
- `GET /severity` — los 21.602 polígonos como GeoJSON (`?severity=` filtra por clase, p. ej. `Severidad alta`)
- `GET /severity/stats` — hectáreas y cantidad de polígonos por clase
- `GET /imagery/rgb_before.png` / `rgb_after.png` — color verdadero antes/después (issue #11)

Visor (React + Vite + Leaflet, issues #10-#11) — necesita la API corriendo:

```bash
cd web
npm install
npm run dev
```

Abre `http://localhost:5173`. Pestaña **Mapa**: los 21.602 polígonos de
`GET /severity` sobre OpenStreetMap, coloreados por clase, con un panel de
hectáreas por clase (`GET /severity/stats`) y un popup por polígono al hacer
clic. Pestaña **Antes / después**: comparador con slider entre las imágenes
de color verdadero antes/después del incendio.

Deploy a Netlify (issue #12) — el frontend desplegado usa datos **estáticos**,
no la API (que solo corre local, con `docker compose`):

```bash
# con la API local corriendo (docker compose up -d + uvicorn):
cd pipeline
python3 export_static.py   # snapshot de /severity, /severity/stats y las
                            # imágenes a web/public/ (GeoJSON simplificado,
                            # imágenes recomprimidas a JPEG)

cd ../web
npm run build               # usa web/public/*.json|geojson|jpg, no la API
npm run preview             # probarlo local antes de pushear
```

`netlify.toml` (en la raíz) le dice a Netlify que la app vive en `web/`: conectar
el repo, base directory `web`, build command `npm run build`, publish dir `dist`.
Los archivos generados por `export_static.py` se commitean (no están en
`.gitignore`, a diferencia de `data/`): Netlify no tiene la base de datos ni la
API para regenerarlos en su propio build.

Tests (no requieren red ni datos reales):

```bash
cd pipeline
python3 -m pytest

cd api
python3 -m pytest
```

## Estado del proyecto

- [x] #1 Estructura del repo y entorno
- [x] #2 Área de estudio y fechas
- [x] #3 Búsqueda de escenas Sentinel-2
- [x] #4 Carga de bandas y máscara de nubes
- [x] #5 NBR, dNBR y clases de severidad
- [x] #6 Vectorización y estadísticas
- [x] #7 Validación
- [x] #8 PostGIS en Docker
- [x] #9 API con FastAPI
- [x] #10 Visor React + Leaflet
- [x] #11 Comparador antes/después y panel
- [x] #12 Deploy
- [ ] #13 README final
- [ ] #14 Preparación de la entrevista
- [ ] #15 Clasificador con machine learning (extra)
