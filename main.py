# ============================================================
# 🇪🇸 SPAIN MOBILE TOWERS API — Versión Avanzada 3.0
# Autor: Antonio Sánchez
# Mejora: Chapi 🤖 (Optimizaciones de compatibilidad, CORS y despliegue)
# ============================================================

from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from collections import Counter
from loguru import logger
import os

# ============================================================
# 🚀 CONFIGURACIÓN INICIAL
# ============================================================

app = FastAPI(
    title="Spain Mobile Towers API",
    version="3.0",
    description=(
        "API pública para consultar antenas móviles en España.\n\n"
        "Incluye búsquedas por operador, localización, radio y estadísticas avanzadas.\n"
        "Fuente oficial: Geoportal del Ministerio de Industria, Comercio y Turismo."
    ),
    root_path=os.getenv("ROOT_PATH", ""),  # 🔧 mejora compatibilidad con Render y proxys
)

# Middleware CORS (para acceso libre desde RapidAPI, Postman, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Acceso universal
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware GZIP (reduce tamaño de respuesta hasta 5×)
app.add_middleware(GZipMiddleware, minimum_size=500)

# ============================================================
# 📦 IMPORTAR UTILIDADES (carga bajo demanda)
# ============================================================

from utils import load_antenas, haversine

# ============================================================
# 🌐 ENDPOINTS PRINCIPALES
# ============================================================

@app.get("/")
def home():
    """🏠 Página de inicio con metadatos y estado."""
    # Carga bajo demanda para no saturar memoria al inicio
    antenas = load_antenas()
    return {
        "message": "📡 Spain Mobile Towers API está en línea.",
        "version": "3.0",
        "author": "Antonio Sánchez",
        "total_antenas": len(antenas),
        "endpoints": [
            "/antenas", 
            "/antenas/near", 
            "/antenas/info", 
            "/antenas/stats/coverage", 
            "/antenas/geojson",
            "/antenas/rankings",
            "/map/stats",           # 🆕 Compatible con dashboard
            "/map/antenas"          # 🆕 Compatible con dashboard
        ],
        "status": "✅ online",
        "compatible_with": "spain-towers-visualizer"  # 🆕 Indicador de compatibilidad
    }


@app.get("/healthz")
def health():
    """❤️ Verifica la salud del servicio (monitorización)."""
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
    # Carga bajo demanda en cada request
    data = load_antenas()

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
        data = [a for a in data if "lat" in a and "lon" in a and lat_min <= a["lat"] <= lat_max and lon_min <= a["lon"] <= lon_max]

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
    # Carga bajo demanda
    antenas = load_antenas()
    
    nearby = [a for a in antenas if "lat" in a and "lon" in a and haversine(lat, lon, a["lat"], a["lon"]) <= radio_m]
    nearby.sort(key=lambda a: haversine(lat, lon, a["lat"], a["lon"]))
    
    return JSONResponse(content=nearby[:limit], media_type="application/json")


# ============================================================
# 📊 ENDPOINTS AVANZADOS
# ============================================================

@app.get("/antenas/info")
def info_operador(operador: str):
    """
    📈 Devuelve resumen estadístico de un operador:
    - Número total de antenas
    - Provincias donde opera
    - Porcentaje relativo de cobertura
    """
    # Carga bajo demanda
    antenas = load_antenas()
    
    data = [a for a in antenas if operador.lower() in a.get("operador", "").lower()]
    if not data:
        raise HTTPException(status_code=404, detail=f"No se encontraron antenas de {operador}.")
    
    provincias = Counter([a["direccion"].split(",")[-1].strip() for a in data])
    
    return {
        "operador": operador,
        "total_antenas": len(data),
        "provincias": dict(provincias),
        "porcentaje_total": round(len(data) / len(antenas) * 100, 2)
    }


@app.get("/antenas/stats/coverage")
def stats_coverage():
    """📡 Estadísticas globales: cuántas antenas hay por operador y provincia."""
    # Carga bajo demanda
    antenas = load_antenas()
    
    op_counter = Counter(a.get("operador", "Desconocido") for a in antenas)
    prov_counter = Counter(a.get("direccion", "").split(",")[-1].strip() for a in antenas)
    
    return {
        "total_antenas": len(antenas),
        "por_operador": dict(op_counter),
        "por_provincia": dict(prov_counter)
    }


@app.get("/antenas/geojson")
def geojson():
    """🌍 Devuelve las antenas en formato GeoJSON (compatible con Mapbox/Leaflet)."""
    # Carga bajo demanda
    antenas = load_antenas()
    
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
        for a in antenas if "lat" in a and "lon" in a
    ]
    
    return {"type": "FeatureCollection", "features": features}


@app.get("/antenas/rankings")
def rankings(top_n: int = 10):
    """
    🏆 Rankings dinámicos:
    - Top provincias por número de antenas
    - Top operadores por cobertura
    """
    # Carga bajo demanda
    antenas = load_antenas()
    
    prov_counter = Counter(a.get("direccion", "").split(",")[-1].strip() for a in antenas)
    op_counter = Counter(a.get("operador", "Desconocido") for a in antenas)
    
    return {
        "top_provincias": prov_counter.most_common(top_n),
        "top_operadores": op_counter.most_common(top_n)
    }


# ============================================================
# 🗺️ ENDPOINTS COMPATIBLES CON DASHBOARD (NUEVOS)
# ============================================================

@app.get("/map/stats")
def get_map_stats():
    """
    📊 Endpoint específico para el dashboard Spain Towers Visualizer.
    
    Proporciona estadísticas en formato optimizado para visualización:
    - Total de antenas
    - Distribución por operador
    - Distribución por tecnología
    
    Compatible con: https://github.com/ajsanchezv92/spain-towers-visualizer
    """
    # Carga bajo demanda - mismo sistema que endpoints existentes
    antenas = load_antenas()
    
    # Calcular estadísticas optimizadas para dashboard
    operadores = {}
    tecnologias = {}
    
    for antenna in antenas:
        op = antenna.get("operador", "Desconocido")
        tech = antenna.get("tecnologia", "Desconocida")
        
        operadores[op] = operadores.get(op, 0) + 1
        tecnologias[tech] = tecnologias.get(tech, 0) + 1
    
    logger.info(f"📈 Estadísticas enviadas al dashboard: {len(antenas)} antenas")
    
    return {
        "total_antenas": len(antenas),
        "por_operador": operadores,
        "por_tecnologia": tecnologias
    }


@app.get("/map/antenas")
def get_map_antenas(
    bbox: str = None,
    operador: str = None,
    tecnologia: str = None,
    limit: int = 500
):
    """
    🗺️ Endpoint específico para el dashboard Spain Towers Visualizer.
    
    Proporciona datos de antenas en formato GeoJSON optimizado para mapas:
    - Filtrado por bounding box (lazy loading)
    - Filtrado por operador/tecnología
    - Formato GeoJSON estándar para Leaflet/Mapbox
    
    Parámetros:
    - bbox: min_lon,min_lat,max_lon,max_lat (para carga por viewport)
    - operador: Filtrar por compañía específica
    - tecnologia: Filtrar por tecnología específica
    - limit: Límite de resultados (optimización de rendimiento)
    """
    # Carga bajo demanda
    antenas = load_antenas()
    
    # Filtrar por bounding box si se proporciona (lazy loading)
    filtered_antenas = antenas
    if bbox:
        try:
            min_lon, min_lat, max_lon, max_lat = map(float, bbox.split(','))
            filtered_antenas = [
                a for a in filtered_antenas
                if "lat" in a and "lon" in a and 
                   min_lon <= a["lon"] <= max_lon and 
                   min_lat <= a["lat"] <= max_lat
            ]
            logger.info(f"📍 Bounding box aplicado: {bbox} -> {len(filtered_antenas)} antenas")
        except ValueError as e:
            logger.warning(f"⚠️ Bounding box inválido: {bbox} - {e}")
            # Continuar sin filtro de bbox en caso de error
    
    # Aplicar filtros adicionales
    if operador:
        filtered_antenas = [a for a in filtered_antenas if a.get("operador") == operador]
        logger.info(f"📡 Filtro operador: {operador} -> {len(filtered_antenas)} antenas")
    
    if tecnologia:
        filtered_antenas = [a for a in filtered_antenas if a.get("tecnologia") == tecnologia]
        logger.info(f"📶 Filtro tecnología: {tecnologia} -> {len(filtered_antenas)} antenas")
    
    # Limitar resultados para optimizar rendimiento del frontend
    result_antenas = filtered_antenas[:limit]
    
    # Convertir a formato GeoJSON estándar para el dashboard
    features = [
        {
            "type": "Feature",
            "geometry": {
                "type": "Point", 
                "coordinates": [a["lon"], a["lat"]]
            },
            "properties": {
                "id": a.get("id", f"antenna_{idx}"),
                "operador": a.get("operador", "Desconocido"),
                "tecnologia": a.get("tecnologia", "Desconocida"),
                "provincia": a.get("direccion", "").split(",")[-1].strip() if a.get("direccion") else "Desconocida"
            }
        }
        for idx, a in enumerate(result_antenas) 
        if "lat" in a and "lon" in a  # Solo antenas con coordenadas válidas
    ]
    
    logger.info(f"🗺️ Enviadas {len(features)} antenas al dashboard")
    
    return {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "total": len(result_antenas),
            "limit": limit,
            "filters_applied": {
                "bbox": bbox is not None,
                "operador": operador is not None,
                "tecnologia": tecnologia is not None
            }
        }
    }


# ============================================================
# ⚠️ MANEJO DE ERRORES
# ============================================================

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


# ============================================================
# 🚀 INICIALIZACIÓN SEGURA
# ============================================================

@app.on_event("startup")
async def startup_event():
    """Inicialización segura que no satura la memoria"""
    logger.info("🚀 Iniciando Spain Mobile Towers API v3.0...")
    logger.info("✅ Compatible con Spain Towers Visualizer Dashboard")
    logger.info("📍 Endpoints /map/stats y /map/antenas disponibles")
    logger.info("💾 Carga de datos bajo demanda activada")
