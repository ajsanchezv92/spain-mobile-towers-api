============================================================

🇪🇸 SPAIN MOBILE TOWERS API — UTILIDADES

Autor: Antonio Sánchez

Mejora: Chapi 🤖 (Carga bajo demanda, funciones auxiliares)

============================================================

import requests
import json
import math
from functools import lru_cache
from loguru import logger
import os
from dotenv import load_dotenv

============================================================

🔧 CARGA DE VARIABLES DE ENTORNO

============================================================

load_dotenv()  # Carga variables desde .env

ANTENAS_URL = os.getenv("ANTENAS_URL", "https://drive.google.com/uc?export=download&id=156kbTsnPQzPh-z0Fz1wc3DdvLEonShKd")

============================================================

🧠 FUNCIONES DE DATOS

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
