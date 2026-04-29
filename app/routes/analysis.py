from flask import Blueprint, jsonify, render_template, request
from app.services.aiService import aiService
from app.services.importExportService import importExportService

analysisBp = Blueprint("analysis", __name__)

@analysisBp.route("/analysis")
def analysisPage():
    return render_template("analysis.html")

@analysisBp.route("/api/analysis/evaluate", methods=["POST"])
def evaluate():
    data = request.get_json(force=True)
    fen = data.get("fen", "")
    timeLimitSeconds = float(data.get("timeLimitSeconds", 1.0))
    maxDepth = int(data.get("maxDepth", 4))
    return jsonify(aiService.analysePosition(fen, timeLimitSeconds, maxDepth))

@analysisBp.route("/api/fen/validate", methods=["POST"])
def validateFen():
    data = request.get_json(force=True)
    return jsonify(importExportService.validateFen(data.get("fen", "")))
