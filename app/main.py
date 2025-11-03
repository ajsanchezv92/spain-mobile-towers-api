from fastapi import FastAPI, Query, HTTPException, Header
from fastapi.responses import JSONResponse
import json
import math
import requests
import os
from collections import Counter
from datetime import datetime, timedelta

app = FastAPI(
    title="Spain Mobile Towers API",
    version="1.2",
    description="API para consultar antenas de telefonía móvil en España con filtros, geolocalización y estadísticas."
)

# URL del dataset en Google Drive
ANTENAS_URL = "https://drive.google.com/uc?export=download&id=156kbTsnPQzPh-z0Fz1wc3DdvLEonShKd"

# Configuración de cache
CACHE_DURATION = timedelta(hours=6)
CACHE_DATA = {"data": None, "last_update": None}

# API key opcional
API_KEY = os.getenv("API_KEY")

# --------------------------
# Funciones auxiliares
# --------------------------

def verify_api_key(x_api_key: str = Header(None)):
    """Verifica la API key si está activada."""
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API key inválida o ausente.")

def load_antenas():
    """Descarga y cachea los datos del JSON."""
    global CACHE_DATA
    now = datetime.utcnow()

    if CACHE_DATA["data"] and CACHE_DATA["last_update"] and now - CACHE_DATA["last_update"] < CACHE_DURATION:
        return CACHE_DATA["data"]

    try:
        print("📡 Descargando antenas desde Google Drive...")
        r = requests.get(ANTENAS_URL, timeout=120)
        r.raise_for_status()
        data = json.loads(r.text)

        # Añadimos ID incremental si no existe
        for i, a in enumerate(data):
            a["id"] = i + 1

        CACHE_DATA = {"data": data, "last_update": now}
        print(f"✅ Antenas cargadas: {len(data)} registros")
        return data
    except Exception as e:
        print(f"❌ Error al descargar antenas: {e}")
        if CACHE_DATA["data"]:
            print("⚠️ Usando datos en cache anteriores.")
            return CACHE_DATA["data"]
        raise HTTPException(status_code=500, detail="Error cargando datos de antenas.")

# Carga inicial
ANTENAS = load_antenas()

# --------------------------
# Endpoints
# --------------------------

@app.get("/healthz")
def health():
    """Verifica el estado general de la API."""
    return {"status": "ok", "message": "API funcionando correctamente."}

@app.get("/antenas")
def list_antenas(
    operador: str = None,
    direccion: str = None,
    archivo_origen: str = None,
    page: int = 1,
    limit: int = 100,
    x_api_key: str = Header(None)
):
    verify_api_key(x_api_key)
    data = load_antenas()
    filtered = data

    if operador:
        filtered = [a for a in filtered if a.get("operador") and operador.lower() in a["operador"].lower()]
    if direccion:
        filtered = [a for a in filtered if a.get("direccion") and direccion.lower() in a["direccion"].lower()]
    if archivo_origen:
        filtered = [a for a in filtered if a.get("archivo_origen") and archivo_origen.lower() in a["archivo_origen"].lower()]

    start, end = (page - 1) * limit, page * limit
    response = JSONResponse(filtered[start:end])
    response.headers["Cache-Control"] = "public, max-age=3600"
    return response

@app.get("/antenas/{antena_id}")
def get_antena(antena_id: int, x_api_key: str = Header(None)):
    verify_api_key(x_api_key)
    data = load_antenas()
    a = next((a for a in data if a.get("id") == antena_id), None)
    if not a:
        raise HTTPException(status_code=404, detail="Antena no encontrada")
    return a

@app.get("/antenas/near")
def antenas_near(
    lat: float = Query(...),
    lon: float = Query(...),
    radio_m: int = Query(5000, ge=100),
    limit: int = Query(50, le=200),
    x_api_key: str = Header(None)
):
    verify_api_key(x_api_key)
    data = load_antenas()

    def distance(a):
        try:
            R = 6371000
            phi1, phi2 = math.radians(lat), math.radians(a["lat"])
            dphi = math.radians(a["lat"] - lat)
            dlambda = math.radians(a["lon"] - lon)
            h = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
            return 2 * R * math.atan2(math.sqrt(h), math.sqrt(1 - h))
        except Exception:
            return float("inf")

    nearby = [a for a in data if a.get("lat") and a.get("lon") and distance(a) <= radio_m]
    nearby.sort(key=distance)
    response = JSONResponse(nearby[:limit])
    response.headers["Cache-Control"] = "public, max-age=600"
    return response

@app.get("/stats")
def stats(x_api_key: str = Header(None)):
    verify_api_key(x_api_key)
    data = load_antenas()
    op_counter = Counter(a["operador"] for a in data if a.get("operador"))
    origen_counter = Counter(a["archivo_origen"] for a in data if a.get("archivo_origen"))
    return {
        "by_operator": dict(op_counter),
        "by_source_file": dict(origen_counter),
        "total_antenas": len(data)
    }
