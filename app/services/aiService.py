from app import db
from app.models import AnalysisRecord, Game
from engine.fen import exportFen, loadFen
from engine.search import Searcher

class AiService:
    def analysePosition(self, fen: str, timeLimitSeconds: float = 1.0, maxDepth: int = 4) -> dict:
        gameState = loadFen(fen)
        result = Searcher().findBestMove(gameState, timeLimitSeconds=timeLimitSeconds, maxDepth=maxDepth)
        record = AnalysisRecord(
            fen=exportFen(gameState),
            bestMove=result.bestMove.basicUci() if result.bestMove else None,
            score=result.score,
            depth=result.depthReached,
            pvLine=" ".join(result.principalVariation),
        )
        db.session.add(record)
        db.session.commit()
        return {
            "fen": exportFen(gameState),
            "bestMove": record.bestMove,
            "scoreCp": result.score,
            "depth": result.depthReached,
            "nodes": result.nodeCount,
            "elapsedMs": result.elapsedMs,
            "principalVariation": result.principalVariation,
            "transpositionHits": result.transpositionHits,
        }

    def chooseAiMove(self, game: Game, timeLimitSeconds: float = 1.0, maxDepth: int = 4):
        gameState = loadFen(game.currentFen)
        return Searcher().findBestMove(gameState, timeLimitSeconds=timeLimitSeconds, maxDepth=maxDepth)

aiService = AiService()
