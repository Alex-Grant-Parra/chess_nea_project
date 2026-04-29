from flask import Blueprint, jsonify, redirect, render_template, request, url_for
from engine.exceptions import GameAlreadyFinishedError, InvalidMoveError
from app.models import Game
from app.services.gameService import gameService

gamesBp = Blueprint("games", __name__)

@gamesBp.route("/")
def index():
    games = Game.query.order_by(Game.startedAt.desc()).limit(10).all()
    return render_template("index.html", games=games)

@gamesBp.route("/game/new", methods=["POST"])
def newGame():
    mode = request.form.get("mode", "local")
    fen = request.form.get("fen") or None
    game = gameService.createGame(mode=mode, startingFen=fen) if fen else gameService.createGame(mode=mode)
    return redirect(url_for("games.gamePage", gameId=game.id))

@gamesBp.route("/game/<int:gameId>")
def gamePage(gameId):
    game = Game.query.get_or_404(gameId)
    return render_template("game.html", game=game)

@gamesBp.route("/api/game/<int:gameId>/state")
def gameState(gameId):
    game = Game.query.get_or_404(gameId)
    return jsonify(gameService.serialiseGame(game))

@gamesBp.route("/api/game/<int:gameId>/move", methods=["POST"])
def submitMove(gameId):
    data = request.get_json(force=True)
    try:
        return jsonify(gameService.submitMove(gameId, data.get("move", "")))
    except InvalidMoveError as error:
        return jsonify({"error": str(error)}), 400
    except GameAlreadyFinishedError as error:
        return jsonify({"error": str(error)}), 409

@gamesBp.route("/api/game/<int:gameId>/legal-moves")
def legalMoves(gameId):
    fromSquare = request.args.get("fromSquare", type=int)
    return jsonify(gameService.getLegalMoves(gameId, fromSquare))
