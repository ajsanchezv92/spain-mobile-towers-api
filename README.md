
<!-- ===================================================== -->
<!-- 🛰️ SPAIN MOBILE TOWERS API - README COMPLETO (v1.2)   -->
<!-- Autor: Antonio Sánchez (Toni)                        -->
<!-- Objetivo: README con SEO, branding y bilingüe 🇪🇸🇬🇧   -->
<!-- ===================================================== -->

# 🛰️ Spain Mobile Towers API 🇪🇸  
[![Public API](https://img.shields.io/badge/Public%20API-Spain%20Towers-blue.svg)](https://spain-mobile-towers-api.onrender.com)
[![Made with FastAPI](https://img.shields.io/badge/Made%20with-FastAPI-green.svg)](https://fastapi.tiangolo.com/)
[![Hosted on Render](https://img.shields.io/badge/Hosted%20on-Render-purple.svg)](https://render.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🇪🇸 Descripción general

**Spain Mobile Towers API** es una API pública que proporciona información sobre **todas las antenas de telefonía móvil en España**, incluyendo coordenadas, operador, tecnología (2G, 3G, 4G, 5G) y dirección exacta.

💡 Ideal para:
- Crear **mapas de cobertura móvil** en tiempo real  
- Analizar **infraestructura de telecomunicaciones**  
- Desarrollar **proyectos IoT, Smart City o de geolocalización**

📍 **Fuente oficial:** Geoportal del Ministerio de Industria de España  
🧠 **Framework:** [FastAPI](https://fastapi.tiangolo.com/)  
☁️ **Hosting:** [Render](https://render.com)

---

## ⚙️ Características principales

✅ Filtros por **operador, provincia, municipio y tecnología**  
✅ Endpoint de **antenas cercanas a coordenadas GPS**  
✅ Estadísticas por operador y tipo de red  
✅ **CORS habilitado** para uso libre desde clientes o RapidAPI  
✅ 100% **open source y gratuita**

---

## 🚀 Enlaces principales

- 🌍 **Base URL:** [https://spain-mobile-towers-api.onrender.com](https://spain-mobile-towers-api.onrender.com)  
- 📘 **Documentación Swagger:** [/docs](https://spain-mobile-towers-api.onrender.com/docs)  
- 📗 **Redoc alternativa:** [/redoc](https://spain-mobile-towers-api.onrender.com/redoc)  
- 💾 **Repositorio GitHub:** [https://github.com/ajsanchezv92/spain-mobile-towers-api](https://github.com/ajsanchezv92/spain-mobile-towers-api)

---

## 📡 Endpoints disponibles (v1.2)

| Endpoint | Descripción | Ejemplo |
|-----------|-------------|----------|
| `/antenas` | Lista todas las antenas | `/antenas` |
| `/antenas/{id}` | Devuelve una antena por su ID | `/antenas/1250` |
| `/antenas?operador=Movistar&provincia=Madrid` | Filtro múltiple por operador y provincia | `/antenas?operador=Orange&municipio=Sevilla` |
| `/antenas/near?lat=40.4167&lon=-3.7033&radio_m=5000` | Antenas cercanas a coordenadas | `/antenas/near?lat=41.4&lon=2.17` |
| `/stats` | Estadísticas agregadas por operador y tecnología | `/stats` |

---

## 🧠 Ejemplos de uso

### 🔹 Obtener antenas de Vodafone en Valencia:
```bash
GET /antenas?operador=Vodafone&provincia=Valencia

🔹 Buscar antenas cercanas a unas coordenadas:

GET /antenas/near?lat=40.4167&lon=-3.7033&radio_m=3000

🔹 Consultar estadísticas por operador y tecnología:

GET /stats


---

🧩 Tecnologías utilizadas

Tecnología	Uso principal

FastAPI	Framework backend ultrarrápido
Uvicorn	Servidor ASGI de alto rendimiento
Requests	Carga dinámica del dataset desde Drive
Pandas	Análisis y agrupación de datos
CORS Middleware	Permitir acceso externo libre
Render	Hosting gratuito y escalable



---

🧭 Roadmap 2025

🔁 Actualización automática semanal desde el Geoportal

🌍 API bilingüe completa (EN + ES)

🧮 Estadísticas avanzadas por operador y cobertura

🗺️ Endpoint GeoJSON para visualizaciones tipo mapa de calor

🔐 Autenticación opcional con API Key (modo Pro)



---

💬 Contribuciones

Las contribuciones son bienvenidas 🙌

1. Haz un fork del proyecto


2. Crea una nueva rama:

git checkout -b feature/nueva-funcionalidad


3. Envía tu pull request con una descripción clara




---

🧑‍💻 Créditos

Proyecto desarrollado por Antonio “Toni” Sánchez
📧 Contacto: contact@yourdomain.com
🐙 GitHub: @ajsanchezv92


---

🌍 English Section — Spain Mobile Towers API 🇬🇧

Spain Mobile Towers API is a public and open API providing information on all mobile network antennas across Spain 🇪🇸.
Includes GPS coordinates, operator name, and network type (2G, 3G, 4G, 5G).

💡 Perfect for:

Building mobile coverage maps

Telecom research and analysis

IoT and Smart City projects


🔧 Core Features

Operator / Province / City filtering

Nearby antennas by GPS location

Aggregated statistics by operator or network

CORS enabled for full public access

Free and open source


🔗 Base URL

https://spain-mobile-towers-api.onrender.com

🔍 Example Usage

GET /antenas?operador=Vodafone&provincia=Barcelona
GET /antenas/near?lat=40.4&lon=-3.7
GET /stats

🧱 Tech Stack

FastAPI

Python 3.12

Render Hosting

Pandas

Requests



---

📈 SEO Keywords

Spanish: antenas móviles España, cobertura móvil, API antenas 5G, operadores móviles, cobertura 4G España, datos abiertos telecomunicaciones.
English: Spain mobile towers, cellular coverage Spain, 5G Spain API, mobile network data, telecom coverage, open data API, coverage map Spain.


---

📜 Licencia

Este proyecto está bajo la licencia MIT, lo que permite su uso libre tanto comercial como educativo.
Consulta el archivo LICENSE para más detalles.


---

<!-- ===================================================== --><!-- ✨ FIN DEL README - Spain Mobile Towers API (Toni)     --><!-- ===================================================== -->---
