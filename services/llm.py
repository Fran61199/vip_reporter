import os
import re
from textwrap import dedent
from openai import OpenAI

SYSTEM_PROMPT = dedent("""\
Eres un médico ocupacional experto. Escribe conclusiones clínicas breves, impersonales y con estilo de informe.
Reglas:
- Enlista hallazgos por especialidad solo si hay evidencia en el texto origen; si no hay dato, omítelo.
- Frases modelo: "La exploración de...", "El examen evidencia...", "La evaluación determina...".
- 1–2 oraciones por especialidad; evita opiniones y recomendaciones salvo la sección final.
- Español neutro, términos clínicos correctos; unidades y rangos cuando existan.
- Cierra con "En conclusión" seguido de 3–5 recomendaciones generales si corresponde.
- No inventes valores. Evita diagnósticos que no aparezcan.
- Si hay valores lipídicos elevados, menciónalos en una línea.
Especialidades comunes: Oftalmología, Cardiovascular/ECG/Prueba de esfuerzo, ORL/Audiometría, Neumología/Espirometría/Rx tórax, Radiología (columna), Odontología, Músculo-esquelético, Ecografía (abdominal/pélvica), Urología/Próstata, Laboratorio.
Salida: texto corrido con párrafos por especialidad; sin títulos en mayúsculas.
""")

def _clean_text(t: str) -> str:
    t = re.sub(r"\s+", " ", t or "").strip()
    return t

def build_report_body(raw_text: str, patient_name: str = "", edad: str = "") -> str:
    
    for var in [
        "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY",
        "http_proxy", "https_proxy", "all_proxy",
        "OPENAI_HTTP_PROXY", "OPENAI_PROXY"
    ]:
        os.environ.pop(var, None)

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        
        raise RuntimeError("Falta OPENAI_API_KEY en las variables de entorno.")

    client = OpenAI(api_key=api_key)

    cleaned = _clean_text(raw_text)[:120000]  
    if not cleaned:
        raise ValueError("No hay texto extraído de los PDFs para enviar al modelo.")

    user_prompt = dedent(f"""\
    Texto fuente (extracto de PDFs de resultados). Resume y redacta como informe final:
    Paciente: {patient_name or '—'}
    Edad reportada: {edad or '—'}
    Texto: ```{cleaned}```
    """)

    model = (os.environ.get("OPENAI_MODEL") or "gpt-4o-mini").strip()

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=1200,
    )

    return (resp.choices[0].message.content or "").strip()
