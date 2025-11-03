# 📡 Spain Mobile Towers API

API pública en **FastAPI** para consultar y analizar antenas de telefonía móvil en toda España.  
Proporciona información sobre ubicación, operador y proximidad de antenas.  
Diseñada para funcionar de forma gratuita en **Render** y poder publicarse fácilmente en **RapidAPI**.

---

## 🚀 Características principales
- Consulta de antenas por provincia, municipio, operador o tecnología.  
- Búsqueda de antenas cercanas a unas coordenadas (`/antenas/near`).  
- Estadísticas globales de operadores y tecnologías (`/stats`).  
- Endpoint de salud (`/healthz`) para monitorización.  
- Datos actualizados procedentes del **Geoportal del Ministerio de Industria**.  

---

## 🧠 Tecnologías
- **FastAPI** (backend moderno y rápido en Python)
- **Uvicorn** (servidor ASGI de alto rendimiento)
- **Requests** (descarga y actualización de datos)
- **Python 3.12**
- **Docker** (para despliegue portátil)

---

## 🛠️ Despliegue en Render

1. **Sube el repositorio** a tu cuenta de GitHub.  
2. En [Render.com](https://render.com):
   - Crea un **nuevo servicio web** → conecta el repositorio.
   - Selecciona el **runtime** de Python 3.12.
3. Render instalará automáticamente las dependencias del archivo `requirements.txt`.
4. En el campo **Start Command**, usa:
