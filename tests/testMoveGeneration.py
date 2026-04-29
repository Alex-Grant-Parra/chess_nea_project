from engine.constants import START_FEN
from engine.fen import exportFen, loadFen
from engine.perft import perft

KIWIPETE = "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1"

def assertMakeUndoStable(fen: str):
    gameState = loadFen(fen)
    originalFen = exportFen(gameState)
    for move in gameState.legalMoves():
        gameState.makeMove(move)
        gameState.undoMove()
        assert exportFen(gameState) == originalFen

def testStartingPositionPerft():
    gameState = loadFen(START_FEN)
    assert perft(gameState, 1) == 20
    assert perft(gameState, 2) == 400
    assert perft(gameState, 3) == 8902

def testKiwipetePerftShallow():
    gameState = loadFen(KIWIPETE)
    assert perft(gameState, 1) == 48
    assert perft(gameState, 2) == 2039

def testMakeUndoStableFromStartingPositionAndKiwipete():
    assertMakeUndoStable(START_FEN)
    assertMakeUndoStable(KIWIPETE)
