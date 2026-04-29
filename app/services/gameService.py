from app import db
from app.models import Game, MoveRecordDb
from engine.constants import START_FEN, GameStatus
from engine.exceptions import GameAlreadyFinishedError, InvalidMoveError
from engine.fen import exportFen, loadFen
from engine.notation import findLegalMoveByUci, generateSanBeforeMove

class GameService:
    def createGame(self, mode: str = "local", startingFen: str = START_FEN) -> Game:
        gameState = loadFen(startingFen)
        game = Game(mode=mode, startingFen=exportFen(gameState), currentFen=exportFen(gameState), status=GameStatus.ACTIVE.value)
        db.session.add(game)
        db.session.commit()
        return game

    def loadGameState(self, game: Game):
        return loadFen(game.currentFen)

    def submitMove(self, gameId: int, moveUci: str, userId: int | None = None) -> dict:
        game = Game.query.get_or_404(gameId)
        if game.status != GameStatus.ACTIVE.value:
            raise GameAlreadyFinishedError("This game is already finished")
        gameState = loadFen(game.currentFen)
        legalMove = findLegalMoveByUci(gameState, moveUci)
        if legalMove is None:
            raise InvalidMoveError("Move is not legal")
        san = generateSanBeforeMove(gameState, legalMove)
        movingColour = gameState.sideToMove.value
        gameState.makeMove(legalMove)
        game.currentFen = exportFen(gameState)
        game.status = gameState.status().value
        db.session.add(MoveRecordDb(
            gameId=game.id,
            moveNumber=len(game.moves) + 1,
            colour=movingColour,
            uci=legalMove.basicUci(),
            san=san,
            fenAfterMove=game.currentFen,
        ))
        db.session.commit()
        return self.serialiseGame(game, gameState)

    def getLegalMoves(self, gameId: int, fromSquare: int | None = None) -> list[dict]:
        game = Game.query.get_or_404(gameId)
        gameState = loadFen(game.currentFen)
        moves = gameState.legalMoves()
        if fromSquare is not None:
            moves = [move for move in moves if move.fromSquare == fromSquare]
        return [self.serialiseMove(move) for move in moves]

    def serialiseGame(self, game: Game, gameState=None) -> dict:
        gameState = gameState or loadFen(game.currentFen)
        return {
            "gameId": game.id,
            "fen": exportFen(gameState),
            "position": [piece.fenSymbol() if piece else None for piece in gameState.board.squares],
            "sideToMove": gameState.sideToMove.value,
            "status": game.status,
            "result": game.result,
            "legalMoves": [move.basicUci() for move in gameState.legalMoves()],
            "moveList": [
                {"number": move.moveNumber, "colour": move.colour, "uci": move.uci, "san": move.san}
                for move in game.moves
            ],
        }

    def serialiseMove(self, move) -> dict:
        return {
            "uci": move.basicUci(),
            "fromSquare": move.fromSquare,
            "toSquare": move.toSquare,
            "promotion": move.promotionPieceType.value if move.promotionPieceType else None,
            "capture": move.capturedPiece is not None,
        }

gameService = GameService()
