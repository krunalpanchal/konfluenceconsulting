from __future__ import annotations

import os
import sys
import base64
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Ensure project root is on Python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from konfluence_ai.fit_engine import evaluate_fit, build_pdf_report, result_to_dict

app = Flask(__name__, static_folder="static")
allowed_origin = os.environ.get("ALLOWED_ORIGIN", "*")

# CORS (lock this down in production by setting ALLOWED_ORIGIN)
CORS(app, resources={r"/*": {"origins": allowed_origin}})


@app.get("/health")
def health():
    return {"status": "ok"}


# Serve the website page from the same service (easy deploy)
@app.get("/")
def home():
    return send_from_directory(app.static_folder, "resume-fit.html")


@app.get("/static/<path:path>")
def static_files(path: str):
    return send_from_directory(app.static_folder, path)


@app.post("/analyze")
def analyze():
    data = request.get_json(force=True) or {}
    resume = data.get("resume", "")
    job = data.get("job", "")
    want_pdf = bool(data.get("pdf", False))
    auto_must = bool(data.get("auto_must_haves", True))

    if len(resume.strip()) < 200 or len(job.strip()) < 200:
        return jsonify({"error": "Resume and Job Description must be at least 200 characters each."}), 400

    result = evaluate_fit(resume, job, use_auto_must_haves=auto_must)
    payload = {"result": result_to_dict(result)}

    if want_pdf:
        pdf_bytes = build_pdf_report(resume, job, result)
        payload["pdf_base64"] = base64.b64encode(pdf_bytes).decode("utf-8")

    return jsonify(payload)

@app.post("/radar.png")
def radar_png():
    data = request.get_json(force=True) or {}
    radar = data.get("radar_values")
    if not isinstance(radar, dict):
        return jsonify({"error": "radar_values missing"}), 400

    # Import here to avoid circular import concerns
    from konfluence_ai.fit_engine import render_radar_png
    png = render_radar_png(radar)

    # Return raw PNG
    return app.response_class(png, mimetype="image/png")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=True)