# Informe VIP – Generador (Flask)

Plataforma mínima pero sólida para:
- Subir **PDFs** de resultados por especialidad
- Extraer texto y pedir a **OpenAI** (chat.completions) que redacte **conclusiones clínicas**
- Entregar **DOCX** final (con plantilla opcional)

## Ejecutar localmente

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # edita OPENAI_API_KEY
python app.py
```

Visita: <http://localhost:5000>

## Variables de entorno

- `OPENAI_API_KEY` (obligatorio)
- `OPENAI_MODEL` (opcional, defecto `gpt-4o-mini`)
- `FLASK_SECRET_KEY` (opcional)
- `UPLOAD_FOLDER` (opcional)
- `TEMPLATE_FOLDER_USER` (opcional)

## Plantilla .docx (opcional)

Puedes subir un `.docx` con marcadores:
```
{{CIUDAD}}, {{FECHA}}, {{DESTINATARIO}}, {{PACIENTE}}, {{HC}}, {{CUERPO}}
```

Si no subes plantilla, se genera un documento por defecto.

## Despliegue en Render.com

1. Sube este repo a GitHub.
2. En Render, crea **New Web Service** desde el repo.
3. Ajusta **runtime**: Python. Render detecta `requirements.txt` y `Procfile`.
4. Añade la variable **OPENAI_API_KEY** en *Environment* (no la subas al repo).
5. Deploy.

> Archivo `render.yaml` incluido para Infra as Code (opcional).

## Notas de precisión clínica
- El modelo **no inventa** si el texto fuente no trae un dato.
- Usa frases impersonales y 1–2 oraciones por especialidad.
- Cierra con recomendaciones generales si corresponde.

## Seguridad
- No se guardan PDFs ni informes en base de datos.
- Los archivos subidos se procesan en memoria y se devuelven como descarga.
