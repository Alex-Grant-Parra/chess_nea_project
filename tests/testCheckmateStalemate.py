from engine.constants import GameStatus
from engine.fen import loadFen


def testCheckmateDetected():
    gameState = loadFen("7k/6Q1/6K1/8/8/8/8/8 b - - 0 1")
    assert gameState.status() == GameStatus.CHECKMATE


def testStalemateDetected():
    gameState = loadFen("7k/5Q2/6K1/8/8/8/8/8 b - - 0 1")
    assert gameState.status() == GameStatus.STALEMATE


def testInsufficientMaterialDetected():
    gameState = loadFen("8/8/8/8/8/8/7k/6K1 w - - 0 1")
    assert gameState.status() == GameStatus.DRAW_INSUFFICIENT
