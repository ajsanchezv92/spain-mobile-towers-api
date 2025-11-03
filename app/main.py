# ============================================================
# 🇪🇸 SPAIN MOBILE TOWERS API — Versión Avanzada 2.1
# 🇪🇸 SPAIN MOBILE TOWERS API — Versión Avanzada 2.1 Optimizada
# Autor: Antonio Sánchez
# Mejora: Chapi 🤖 (Optimizaciones de compatibilidad, CORS y despliegue)
# Mejora: Chapi 🤖 (Carga bajo demanda para Render Free, compatibilidad y CORS)
# ============================================================

from fastapi import FastAPI, Query, HTTPException, Request
@@ -51,7 +51,10 @@

@lru_cache(maxsize=2)
def load_antenas():
    """📡 Descarga el JSON y lo cachea en memoria (mejora de rendimiento)."""
    """
    📡 Descarga el JSON y lo cachea en memoria bajo demanda.
    🔹 Evita cargar todo en memoria al inicio (resuelve error 502 en Render Free)
    """
    logger.info("📡 Descargando antenas desde Google Drive...")
    try:
        r = requests.get(ANTENAS_URL, timeout=120)
@@ -63,9 +66,6 @@ def load_antenas():
        logger.error(f"❌ Error cargando antenas: {e}")
        return []

# Carga inicial (queda cacheada)
ANTENAS = load_antenas()

# ============================================================
# 🌍 FUNCIONES AUXILIARES
# ============================================================
@@ -86,11 +86,12 @@ def haversine(lat1, lon1, lat2, lon2):
@app.get("/")
def home():
    """🏠 Página de inicio con metadatos y estado."""
    antenas_count = len(load_antenas())
    return {
        "message": "📡 Spain Mobile Towers API está en línea.",
        "version": "2.1",
        "author": "Antonio Sánchez",
        "total_antenas": len(ANTENAS),
        "total_antenas": antenas_count,
        "endpoints": ["/antenas", "/antenas/near", "/antenas/info", "/antenas/stats/coverage", "/antenas/geojson"],
        "status": "✅ online",
    }
@@ -120,7 +121,7 @@ def list_antenas(
    Ejemplo:
      /antenas?operador=Movistar&provincia=Madrid&page=1&limit=50
    """
    data = ANTENAS
    data = load_antenas()  # 🔹 ahora se carga bajo demanda

    # Filtros dinámicos
    if provincia:
@@ -151,7 +152,8 @@ def antenas_near(
    limit: int = Query(50, description="Número máximo de resultados")
):
    """🔎 Busca antenas cercanas a unas coordenadas usando la fórmula de Haversine."""
    nearby = [a for a in ANTENAS if "lat" in a and "lon" in a and haversine(lat, lon, a["lat"], a["lon"]) <= radio_m]
    data = load_antenas()
    nearby = [a for a in data if "lat" in a and "lon" in a and haversine(lat, lon, a["lat"], a["lon"]) <= radio_m]
    nearby.sort(key=lambda a: haversine(lat, lon, a["lat"], a["lon"]))
    return JSONResponse(content=nearby[:limit], media_type="application/json")

@@ -168,25 +170,26 @@ def info_operador(operador: str):
    - Provincias donde opera
    - Porcentaje relativo de cobertura
    """
    data = [a for a in ANTENAS if operador.lower() in a.get("operador", "").lower()]
    data = [a for a in load_antenas() if operador.lower() in a.get("operador", "").lower()]
    if not data:
        raise HTTPException(status_code=404, detail=f"No se encontraron antenas de {operador}.")
    provincias = Counter([a["direccion"].split(",")[-1].strip() for a in data])
    return {
        "operador": operador,
        "total_antenas": len(data),
        "provincias": dict(provincias),
        "porcentaje_total": round(len(data) / len(ANTENAS) * 100, 2)
        "porcentaje_total": round(len(data) / len(load_antenas()) * 100, 2)
    }


@app.get("/antenas/stats/coverage")
def stats_coverage():
    """📡 Estadísticas globales: cuántas antenas hay por operador y provincia."""
    op_counter = Counter(a.get("operador", "Desconocido") for a in ANTENAS)
    prov_counter = Counter(a.get("direccion", "").split(",")[-1].strip() for a in ANTENAS)
    data = load_antenas()
    op_counter = Counter(a.get("operador", "Desconocido") for a in data)
    prov_counter = Counter(a.get("direccion", "").split(",")[-1].strip() for a in data)
    return {
        "total_antenas": len(ANTENAS),
        "total_antenas": len(data),
        "por_operador": dict(op_counter),
        "por_provincia": dict(prov_counter)
    }
@@ -195,6 +198,7 @@ def stats_coverage():
@app.get("/antenas/geojson")
def geojson():
    """🌍 Devuelve las antenas en formato GeoJSON (compatible con Mapbox/Leaflet)."""
    data = load_antenas()
    features = [
        {
            "type": "Feature",
@@ -205,7 +209,7 @@ def geojson():
                "url": a.get("url")
            },
        }
        for a in ANTENAS if "lat" in a and "lon" in a
        for a in data if "lat" in a and "lon" in a
    ]
    return {"type": "FeatureCollection", "features": features}

@@ -217,8 +221,9 @@ def rankings(top_n: int = 10):
    - Top provincias por número de antenas
    - Top operadores por cobertura
    """
    prov_counter = Counter(a.get("direccion", "").split(",")[-1].strip() for a in ANTENAS)
    op_counter = Counter(a.get("operador", "Desconocido") for a in ANTENAS)
    data = load_antenas()
    prov_counter = Counter(a.get("direccion", "").split(",")[-1].strip() for a in data)
    op_counter = Counter(a.get("operador", "Desconocido") for a in data)
    return {
        "top_provincias": prov_counter.most_common(top_n),
        "top_operadores": op_counter.most_common(top_n)
