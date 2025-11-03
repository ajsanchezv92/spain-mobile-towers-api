============================================================

🇪🇸 SPAIN MOBILE TOWERS API — Versión Avanzada 2.1 Optimizada

Autor: Antonio Sánchez

Mejora: Chapi 🤖 (Carga bajo demanda para Render Free, compatibilidad y CORS)

============================================================

from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from functools import lru_cache
from collections import Counter
from loguru import logger
import json
import math
import requests
import os

============================================================

🚀 CONFIGURACIÓN INICIAL

============================================================

app = FastAPI(
title="Spain Mobile Towers API",
version="2.1",
description=(
"API pública para consultar antenas móviles en España.\n\n"
"Incluye búsquedas por operador, localización, radio y estadísticas avanzadas.\n"
"Fuente oficial: Geoportal del Ministerio de Industria, Comercio y Turismo."
),
root_path=os.getenv("ROOT_PATH", ""),  # 🔧 mejora compatibilidad con Render y proxys
)

Middleware CORS (para acceso libre desde RapidAPI, Postman, etc.)

app.add_middleware(
CORSMiddleware,
allow_origins=[""],  # Acceso universal
allow_methods=[""],
allow_headers=["*"],
)

Middleware GZIP (reduce tamaño de respuesta hasta 5×)

app.add_middleware(GZipMiddleware, minimum_size=500)

URL del dataset alojado en Google Drive

ANTENAS_URL = "https://drive.google.com/uc?export=download&id=156kbTsnPQzPh-z0Fz1wc3DdvLEonShKd"

============================================================

🧠 UTILIDADES Y CARGA DE DATOS

============================================================

@lru_cache(maxsize=2)
def load_antenas():
"""
📡 Descarga el JSON y lo cachea en memoria bajo demanda.
🔹 Evita cargar todo en memoria al inicio (resuelve error 502 en Render Free)
"""
logger.info("📡 Descargando antenas desde Google Drive...")
try:
r = requests.get(ANTENAS_URL, timeout=120)
r.raise_for_status()
data = json.loads(r.text)
logger.success(f"✅ Antenas cargadas correctamente: {len(data)} registros")
return data
except Exception as e:
logger.error(f"❌ Error cargando antenas: {e}")
return []

============================================================

🌍 FUNCIONES AUXILIARES

============================================================

def haversine(lat1, lon1, lat2, lon2):
"""Calcula la distancia (en metros) entre dos coordenadas GPS."""
R = 6371000
phi1, phi2 = math.radians(lat1), math.radians(lat2)
dphi = math.radians(lat2 - lat1)
dlambda = math.radians(lon2 - lon1)
a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

============================================================

🌐 ENDPOINTS PRINCIPALES

============================================================

@app.get("/")
def home():
"""🏠 Página de inicio con metadatos y estado."""
antenas_count = len(load_antenas())
return {
"message": "📡 Spain Mobile Towers API está en línea.",
"version": "2.1",
"author": "Antonio Sánchez",
"total_antenas": antenas_count,
"endpoints": ["/antenas", "/antenas/near", "/antenas/info", "/antenas/stats/coverage", "/antenas/geojson"],
"status": "✅ online",
}

@app.get("/healthz")
def health():
"""Verifica la salud del servicio (monitorización)."""
return {"status": "ok"}

@app.get("/antenas")
def list_antenas(
provincia: str | None = None,
municipio: str | None = None,
operador: str | None = None,
tecnologia: str | None = None,
lat_min: float | None = None,
lat_max: float | None = None,
lon_min: float | None = None,
lon_max: float | None = None,
page: int = 1,
limit: int = 100
):
"""
📋 Lista antenas filtrando por múltiples campos combinados.
Ejemplo:
/antenas?operador=Movistar&provincia=Madrid&page=1&limit=50
"""
data = load_antenas()  # 🔹 ahora se carga bajo demanda

# Filtros dinámicos
if provincia:
    data = [a for a in data if provincia.lower() in a.get("direccion", "").lower()]
if municipio:
    data = [a for a in data if municipio.lower() in a.get("direccion", "").lower()]
if operador:
    data = [a for a in data if operador.lower() in a.get("operador", "").lower()]
if tecnologia:
    data = [a for a in data if tecnologia.lower() in a.get("tecnologia", "").lower()]
if lat_min and lat_max and lon_min and lon_max:
    data = [a for a in data if lat_min <= a["lat"] <= lat_max and lon_min <= a["lon"] <= lon_max]

# Paginación
start, end = (page - 1) * limit, page * limit
results = data[start:end]

if not results:
    raise HTTPException(status_code=404, detail="No se encontraron antenas con esos filtros.")
return JSONResponse(content=results, media_type="application/json")

@app.get("/antenas/near")
def antenas_near(
lat: float = Query(..., description="Latitud en grados decimales"),
lon: float = Query(..., description="Longitud en grados decimales"),
radio_m: int = Query(5000, description="Radio de búsqueda en metros"),
limit: int = Query(50, description="Número máximo de resultados")
):
"""🔎 Busca antenas cercanas a unas coordenadas usando la fórmula de Haversine."""
data = load_antenas()
nearby = [a for a in data if "lat" in a and "lon" in a and haversine(lat, lon, a["lat"], a["lon"]) <= radio_m]
nearby.sort(key=lambda a: haversine(lat, lon, a["lat"], a["lon"]))
return JSONResponse(content=nearby[:limit], media_type="application/json")

============================================================

📊 ENDPOINTS AVANZADOS (nuevos)

============================================================

@app.get("/antenas/info")
def info_operador(operador: str):
"""
📈 Devuelve resumen estadístico de un operador:
- Número total de antenas
- Provincias donde opera
- Porcentaje relativo de cobertura
"""
data = [a for a in load_antenas() if operador.lower() in a.get("operador", "").lower()]
if not data:
raise HTTPException(status_code=404, detail=f"No se encontraron antenas de {operador}.")
provincias = Counter([a["direccion"].split(",")[-1].strip() for a in data])
return {
"operador": operador,
"total_antenas": len(data),
"provincias": dict(provincias),
"porcentaje_total": round(len(data) / len(load_antenas()) * 100, 2)
}

@app.get("/antenas/stats/coverage")
def stats_coverage():
"""📡 Estadísticas globales: cuántas antenas hay por operador y provincia."""
data = load_antenas()
op_counter = Counter(a.get("operador", "Desconocido") for a in data)
prov_counter = Counter(a.get("direccion", "").split(",")[-1].strip() for a in data)
return {
"total_antenas": len(data),
"por_operador": dict(op_counter),
"por_provincia": dict(prov_counter)
}

@app.get("/antenas/geojson")
def geojson():
"""🌍 Devuelve las antenas en formato GeoJSON (compatible con Mapbox/Leaflet)."""
data = load_antenas()
features = [
{
"type": "Feature",
"geometry": {"type": "Point", "coordinates": [a["lon"], a["lat"]]},
"properties": {
"direccion": a.get("direccion"),
"operador": a.get("operador"),
"url": a.get("url")
},
}
for a in data if "lat" in a and "lon" in a
]
return {"type": "FeatureCollection", "features": features}

@app.get("/antenas/rankings")
def rankings(top_n: int = 10):
"""
🏆 Rankings dinámicos:
- Top provincias por número de antenas
- Top operadores por cobertura
"""
data = load_antenas()
prov_counter = Counter(a.get("direccion", "").split(",")[-1].strip() for a in data)
op_counter = Counter(a.get("operador", "Desconocido") for a in data)
return {
"top_provincias": prov_counter.most_common(top_n),
"top_operadores": op_counter.most_common(top_n)
}

============================================================

⚠️ MANEJO DE ERRORES

============================================================

@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
logger.warning(f"⚠️ {exc.detail}")
return JSONResponse(
status_code=exc.status_code,
content={"error": exc.detail, "status": exc.status_code},
)

@app.exception_handler(Exception)
def generic_exception_handler(request: Request, exc: Exception):
logger.exception(f"💥 Error interno: {exc}")
return JSONResponse(
status_code=500,
content={"error": "Error interno del servidor", "detail": str(exc)},
)
