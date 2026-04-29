from flask import Blueprint, jsonify, render_template, request
from app.services.puzzleService import puzzleService

puzzlesBp = Blueprint("puzzles", __name__)

@puzzlesBp.route("/puzzles")
def puzzlesPage():
    return render_template("puzzles.html")

@puzzlesBp.route("/api/puzzles/next")
def nextPuzzle():
    puzzle = puzzleService.getNextPuzzle()
    if puzzle is None:
        return jsonify({"error": "No puzzles have been seeded"}), 404
    return jsonify({
        "id": puzzle.id,
        "fen": puzzle.fen,
        "theme": puzzle.theme,
        "difficulty": puzzle.difficulty,
        "moveIndex": 0,
    })

@puzzlesBp.route("/api/puzzles/<int:puzzleId>/move", methods=["POST"])
def puzzleMove(puzzleId):
    data = request.get_json(force=True)
    return jsonify(puzzleService.submitPuzzleMove(
        puzzleId,
        data.get("move", ""),
        data.get("fen", ""),
        int(data.get("moveIndex", 0)),
    ))
