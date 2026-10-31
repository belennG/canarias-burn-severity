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

(Los pasos para correr el pipeline completo se irán documentando aquí a medida que se
implementen los issues #3–#6.)

## Estado del proyecto

- [x] #1 Estructura del repo y entorno
- [x] #2 Área de estudio y fechas
- [ ] #3 Búsqueda de escenas Sentinel-2
- [ ] #4 Carga de bandas y máscara de nubes
- [ ] #5 NBR, dNBR y clases de severidad
- [ ] #6 Vectorización y estadísticas
- [ ] #7 Validación
- [ ] #8 PostGIS en Docker
- [ ] #9 API con FastAPI
- [ ] #10 Visor React + Leaflet
- [ ] #11 Comparador antes/después y panel
- [ ] #12 Deploy
- [ ] #13 README final
- [ ] #14 Preparación de la entrevista
- [ ] #15 Clasificador con machine learning (extra)
