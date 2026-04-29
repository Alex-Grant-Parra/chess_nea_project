import json
from app import db
from app.models import Puzzle
from engine.fen import exportFen, loadFen
from engine.notation import findLegalMoveByUci

class PuzzleService:
    def getNextPuzzle(self) -> Puzzle | None:
        return Puzzle.query.order_by(Puzzle.difficulty.asc(), Puzzle.id.asc()).first()

    def submitPuzzleMove(self, puzzleId: int, moveUci: str, currentFen: str, moveIndex: int) -> dict:
        puzzle = Puzzle.query.get_or_404(puzzleId)
        solution = json.loads(puzzle.solutionMoves)
        if moveIndex >= len(solution):
            return {"correct": False, "completed": True, "message": "Puzzle already complete"}
        expectedMove = solution[moveIndex]
        if moveUci != expectedMove:
            return {"correct": False, "completed": False, "message": "Try again"}
        gameState = loadFen(currentFen)
        move = findLegalMoveByUci(gameState, moveUci)
        if move is None:
            return {"correct": False, "completed": False, "message": "Move is illegal in this position"}
        gameState.makeMove(move)
        moveIndex += 1
        opponentReply = None
        if moveIndex < len(solution):
            opponentReply = solution[moveIndex]
            replyMove = findLegalMoveByUci(gameState, opponentReply)
            if replyMove is not None:
                gameState.makeMove(replyMove)
                moveIndex += 1
        return {
            "correct": True,
            "completed": moveIndex >= len(solution),
            "fen": exportFen(gameState),
            "moveIndex": moveIndex,
            "opponentReply": opponentReply,
        }

puzzleService = PuzzleService()
