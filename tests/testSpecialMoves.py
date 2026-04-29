from engine.constants import PieceType
from engine.fen import exportFen, loadFen


def testWhiteKingsideCastling():
    gameState = loadFen("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    move = next(move for move in gameState.legalMoves() if move.basicUci() == "e1g1")
    assert move.isCastleKingside
    gameState.makeMove(move)
    assert exportFen(gameState).startswith("r3k2r/8/8/8/8/8/8/R4RK1 b kq - 1 1")


def testEnPassantCapture():
    gameState = loadFen("8/8/8/3pP3/8/8/8/4K2k w - d6 0 1")
    move = next(move for move in gameState.legalMoves() if move.basicUci() == "e5d6")
    assert move.isEnPassant
    gameState.makeMove(move)
    assert exportFen(gameState) == "8/8/3P4/8/8/8/8/4K2k b - - 0 1"


def testPromotionCreatesFourChoices():
    gameState = loadFen("4k3/P7/8/8/8/8/8/4K3 w - - 0 1")
    promotions = sorted(move.basicUci() for move in gameState.legalMoves() if move.fromSquare == 48)
    assert promotions == ["a7a8b", "a7a8n", "a7a8q", "a7a8r"]
    queenMove = next(move for move in gameState.legalMoves() if move.basicUci() == "a7a8q")
    gameState.makeMove(queenMove)
    assert gameState.board.getPiece(56).pieceType == PieceType.QUEEN
