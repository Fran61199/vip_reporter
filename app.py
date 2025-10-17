import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import io

from utils.pdf_reader import extract_text_from_pdfs
from services.llm import build_report_body
from report.docx_writer import build_docx_from_body, fill_template_docx

# --- App config ---
load_dotenv()
UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "uploads")
TEMPLATE_FOLDER_USER = os.environ.get("TEMPLATE_FOLDER_USER", "user_templates")
ALLOWED_EXTENSIONS = {"pdf", "docx"}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEMPLATE_FOLDER_USER, exist_ok=True)

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "pdfs" not in request.files:
        flash("No se adjuntaron archivos.")
        return redirect(url_for("index"))

    pdf_files = request.files.getlist("pdfs")
    saved_paths = []
    for f in pdf_files:
        if f and allowed_file(f.filename) and f.filename.lower().endswith(".pdf"):
            filename = secure_filename(f.filename)
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            f.save(path)
            saved_paths.append(path)

    template_file = request.files.get("template_docx")
    template_path = None
    if template_file and allowed_file(template_file.filename) and template_file.filename.lower().endswith(".docx"):
        tname = secure_filename(template_file.filename)
        template_path = os.path.join(TEMPLATE_FOLDER_USER, tname)
        template_file.save(template_path)

    # Patient metadata
    city = request.form.get("city", "Lima")
    date_str = request.form.get("date_str") or datetime.now().strftime("%d de %B del %Y")
    addressee = request.form.get("addressee", "").strip()
    name = request.form.get("patient_name", "").strip()
    hc = request.form.get("hc", "").strip()
    edad = request.form.get("edad", "").strip()

    if not saved_paths:
        flash("Sube al menos un PDF de resultados.")
        return redirect(url_for("index"))

    # Read PDFs and call LLM
    raw_text = extract_text_from_pdfs(saved_paths)
    body = build_report_body(raw_text, patient_name=name, edad=edad)

    # Build DOCX (template first if provided)
    if template_path:
        doc_bytes = fill_template_docx(
            template_path=template_path,
            ciudad=city,
            fecha=date_str,
            destinatario=addressee,
            paciente=name,
            hc=hc,
            body=body
        )
    else:
        doc_bytes = build_docx_from_body(
            ciudad=city,
            fecha=date_str,
            destinatario=addressee,
            paciente=name,
            hc=hc,
            body=body
        )

    out_filename = f"Informe_{secure_filename(name or 'PacienteVIP')}_{datetime.now().strftime('%Y%m%d_%H%M')}.docx"
    return send_file(
        io.BytesIO(doc_bytes),
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        as_attachment=True,
        download_name=out_filename
    )

if __name__ == "__main__":
    # Local dev
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
