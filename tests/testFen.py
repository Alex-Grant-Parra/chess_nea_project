from engine.constants import START_FEN
from engine.fen import exportFen, loadFen

def testStartingFenRoundTrip():
    gameState = loadFen(START_FEN)
    assert exportFen(gameState) == START_FEN

def testFenAfterCommonOpeningMoves():
    gameState = loadFen(START_FEN)
    for uci in ["e2e4", "e7e5", "g1f3", "b8c6"]:
        move = next(move for move in gameState.legalMoves() if move.basicUci() == uci)
        gameState.makeMove(move)
    assert exportFen(gameState) == "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3"
