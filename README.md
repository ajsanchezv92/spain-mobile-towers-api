# Spain Mobile Towers API


API pública para consultar antenas móviles en España. Lista para desplegar gratis en Render y publicar en RapidAPI.


## Despliegue
1. Subir repositorio a GitHub.
2. Crear servicio en Render.com → conectar GitHub → desplegar.
3. Ejecutar `python extractor.py` al menos una vez para generar `antenas.json`.
4. Configurar job diario en Render para actualizar datos automáticamente.
5. Copiar URL HTTPS generado y registrar en RapidAPI.
