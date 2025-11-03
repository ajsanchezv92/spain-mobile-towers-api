from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import math
from collections import Counter
import requests

# ============================================================
# 🚀 CONFIGURACIÓN INICIAL
# ============================================================

app = FastAPI(
    title="Spain Mobile Towers API",
    version="1.1",
    description=(
        "API pública para consultar antenas móviles en España.\n\n"
        "Permite filtrar por operador, provincia, municipio, y localizar antenas cercanas.\n"
        "Fuente oficial: Geoportal del Ministerio de Industria."
    ),
)

# Habilitar CORS para acceso desde RapidAPI u otros clientes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# URL directa del dataset JSON (Google Drive)
ANTENAS_URL = "https://drive.google.com/uc?export=download&id=156kbTsnPQzPh-z0Fz1wc3DdvLEonShKd"

# ============================================================
# 📥 CARGA DE DATOS
# ============================================================

def load_antenas():
    """Descarga el JSON desde Google Drive y lo carga en memoria."""
    print("📡 Descargando antenas desde Google Drive...")
    try:
        r = requests.get(ANTENAS_URL, timeout=120)
        r.raise_for_status()
        data = json.loads(r.text)
        print(f"✅ Antenas cargadas correctamente: {len(data)} registros")
        return data
    except Exception as e:
        print(f"❌ Error cargando antenas: {e}")
        return []

# Cargar datos al iniciar
ANTENAS = load_antenas()

# ============================================================
# 🌐 ENDPOINTS PRINCIPALES
# ============================================================

@app.get("/")
def home():
    """Página de inicio con metadatos básicos."""
    return {
        "message": "📡 Spain Mobile Towers API está en línea.",
        "version": "1.1",
        "author": "Antonio Sánchez",
        "docs_url": "/docs",
        "total_antenas": len(ANTENAS),
        "status": "✅ online",
    }


@app.get("/healthz")
def health():
    """Verifica el estado del servicio."""
    return {"status": "ok"}


@app.get("/antenas")
def list_antenas(
    provincia: str | None = None,
    municipio: str | None = None,
    operador: str | None = None,
    tecnologia: str | None = None,
    page: int = 1,
    limit: int = 100
):
    """Lista antenas con filtros opcionales."""
    filtered = ANTENAS

    # Aplicar filtros dinámicos
    if provincia:
        filtered = [a for a in filtered if provincia.lower() in a.get("direccion", "").lower()]
    if municipio:
        filtered = [a for a in filtered if municipio.lower() in a.get("direccion", "").lower()]
    if operador:
        filtered = [a for a in filtered if operador.lower() in a.get("operador", "").lower()]
    if tecnologia:
        filtered = [a for a in filtered if tecnologia.lower() in a.get("tecnologia", "").lower()]

    # Paginación
    start = (page - 1) * limit
    end = start + limit
    results = filtered[start:end]

    if not results:
        raise HTTPException(status_code=404, detail="No se encontraron antenas con esos filtros.")
    return JSONResponse(results)


@app.get("/antenas/{antena_id}")
def get_antena(antena_id: int):
    """Obtiene información detallada de una antena por su ID."""
    a = next((a for a in ANTENAS if a.get("id") == antena_id), None)
    if not a:
        raise HTTPException(status_code=404, detail="Antena no encontrada.")
    return a


@app.get("/antenas/near")
def antenas_near(
    lat: float = Query(..., description="Latitud en grados decimales"),
    lon: float = Query(..., description="Longitud en grados decimales"),
    radio_m: int = Query(5000, description="Radio de búsqueda en metros"),
    limit: int = Query(50, description="Número máximo de resultados")
):
    """Busca antenas cercanas a unas coordenadas dadas."""
    def distance(a):
        R = 6371000  # radio terrestre en metros
        phi1 = math.radians(lat)
        phi2 = math.radians(a["lat"])
        dphi = math.radians(a["lat"] - lat)
        dlambda = math.radians(a["lon"] - lon)
        h = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        return 2 * R * math.atan2(math.sqrt(h), math.sqrt(1 - h))

    nearby = [a for a in ANTENAS if a.get("lat") and a.get("lon") and distance(a) <= radio_m]
    nearby.sort(key=distance)
    return JSONResponse(nearby[:limit])


@app.get("/stats")
def stats():
    """Devuelve estadísticas agregadas por operador y tecnología."""
    op_counter = Counter(a.get("operador", "Desconocido") for a in ANTENAS)
    tech_counter = Counter(a.get("tecnologia", "Desconocida") for a in ANTENAS if a.get("tecnologia"))
    return {
        "by_operator": dict(op_counter),
        "by_technology": dict(tech_counter)
    }

# ============================================================
# 🧩 MANEJO DE ERRORES PERSONALIZADO
# ============================================================

@app.exception_handler(HTTPException)
def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status": exc.status_code},
    )


@app.exception_handler(Exception)
def generic_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Error interno del servidor", "detail": str(exc)},
    )
