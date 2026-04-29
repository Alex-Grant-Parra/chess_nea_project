from engine.fen import loadFen
from engine.search import Searcher


def testSearchReturnsLegalMoveFromStart():
    gameState = loadFen()
    result = Searcher().findBestMove(gameState, timeLimitSeconds=0.25, maxDepth=2)
    assert result.bestMove is not None
    assert result.bestMove.basicUci() in [move.basicUci() for move in gameState.legalMoves()]
    assert result.nodeCount > 0


def testSearchFindsSimpleMateInOne():
    gameState = loadFen("6k1/5ppp/8/8/8/8/5PPP/5RK1 w - - 0 1")
    result = Searcher().findBestMove(gameState, timeLimitSeconds=0.5, maxDepth=2)
    assert result.bestMove is not None
    assert result.bestMove.basicUci() == "f1e1"
