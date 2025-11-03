# ============================================================
# utils.py
# Funciones auxiliares para Spain Mobile Towers API - Streaming
# ============================================================

import requests
import json
import math
from loguru import logger

ANTENAS_URL = "https://drive.google.com/uc?export=download&id=156kbTsnPQzPh-z0Fz1wc3DdvLEonShKd"

def haversine(lat1, lon1, lat2, lon2):
    """Calcula la distancia (en metros) entre dos coordenadas GPS."""
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def stream_antenas():
    """📡 Descarga el JSON desde Google Drive y lo parsea línea por línea para streaming"""
    logger.info("📡 Descargando antenas en streaming...")
    try:
        with requests.get(ANTENAS_URL, stream=True, timeout=120) as r:
            r.raise_for_status()
            buffer = ""
            for chunk in r.iter_content(chunk_size=8192, decode_unicode=True):
                buffer += chunk
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if line.startswith("{") and line.endswith("}"):
                        yield json.loads(line)
            if buffer.strip().startswith("{") and buffer.strip().endswith("}"):
                yield json.loads(buffer.strip())
    except Exception as e:
        logger.error(f"❌ Error en streaming de antenas: {e}")
        return
