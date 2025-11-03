import requests
import json


WFS_URL = 'https://geoportal.minetur.gob.es/VCTEL/services/QUERY_SERVICE/MapServer/WFSServer?service=WFS&request=GetFeature&typeName=vctel:estacionestelefonia&outputFormat=application/json'


def fetch_antenas():
print('Descargando datos de MINETUR...')
r = requests.get(WFS_URL, timeout=30)
r.raise_for_status()
data = r.json()
features = data.get('features', [])
antenas = []
for f in features:
props = f.get('properties', {})
geom = f.get('geometry')
antenas.append({
'id': props.get('OBJECTID'),
'operador': props.get('OPERADOR'),
'tecnologia': props.get('TECNOLOGIA'),
'banda': props.get('BANDA'),
'provincia': props.get('PROVINCIA'),
'municipio': props.get('MUNICIPIO'),
'direccion': props.get('DIRECCION'),
'lat': geom['coordinates'][1] if geom else None,
'lon': geom['coordinates'][0] if geom else None
})
print(f'Total antenas descargadas: {len(antenas)}')
return antenas


if __name__ == '__main__':
antenas = fetch_antenas()
with open('antenas.json', 'w', encoding='utf-8') as f:
json.dump(antenas, f, ensure_ascii=False)
