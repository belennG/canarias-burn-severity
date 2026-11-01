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
```

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
- `GET /severity` — los 12.982 polígonos como GeoJSON (`?severity=` filtra por clase, p. ej. `Severidad alta`)
- `GET /severity/stats` — hectáreas y cantidad de polígonos por clase

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
- [ ] #10 Visor React + Leaflet
- [ ] #11 Comparador antes/después y panel
- [ ] #12 Deploy
- [ ] #13 README final
- [ ] #14 Preparación de la entrevista
- [ ] #15 Clasificador con machine learning (extra)
