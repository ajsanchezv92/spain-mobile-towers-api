from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
import json
import math
from collections import Counter
import os

app = FastAPI(title='Spain Mobile Towers API', version='1.0')

# Ruta segura del JSON
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, 'antenas.json')

# Cargar datos en memoria
with open(JSON_PATH, 'r', encoding='utf-8') as f:
    ANTENAS = json.load(f)


@app.get('/healthz')
def health():
    return {'status': 'ok'}


@app.get('/antenas')
def list_antenas(
    provincia: str = None,
    municipio: str = None,
    operador: str = None,
    tecnologia: str = None,
    page: int = 1,
    limit: int = 100
):
    filtered = ANTENAS
    if provincia:
        filtered = [a for a in filtered if a['provincia'] and provincia.lower() in a['provincia'].lower()]
    if municipio:
        filtered = [a for a in filtered if a['municipio'] and municipio.lower() in a['municipio'].lower()]
    if operador:
        filtered = [a for a in filtered if a['operador'] and operador.lower() in a['operador'].lower()]
    if tecnologia:
        filtered = [a for a in filtered if a['tecnologia'] and tecnologia.lower() in a['tecnologia'].lower()]

    start = (page - 1) * limit
    end = start + limit
    return JSONResponse(filtered[start:end])


@app.get('/antenas/{antena_id}')
def get_antena(antena_id: int):
    a = next((a for a in ANTENAS if a['id'] == antena_id), None)
    if not a:
        raise HTTPException(status_code=404, detail='Antena no encontrada')
    return a


@app.get('/antenas/near')
def antenas_near(
    lat: float = Query(...),
    lon: float = Query(...),
    radio_m: int = Query(5000),
    limit: int = Query(50)
):
    def distance(a):
        R = 6371000
        phi1 = math.radians(lat)
        phi2 = math.radians(a['lat'])
        dphi = math.radians(a['lat'] - lat)
        dlambda = math.radians(a['lon'] - lon)
        h = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        return 2 * R * math.atan2(math.sqrt(h), math.sqrt(1 - h))

    nearby = [a for a in ANTENAS if a['lat'] and a['lon'] and distance(a) <= radio_m]
    nearby.sort(key=distance)
    return JSONResponse(nearby[:limit])


@app.get('/stats')
def stats():
    tech_counter = Counter(a['tecnologia'] for a in ANTENAS if a['tecnologia'])
    op_counter = Counter(a['operador'] for a in ANTENAS if a['operador'])
    return {'by_technology': tech_counter, 'by_operator': op_counter}
