from engine.constants import Colour, PieceType
from engine.move import Move
from engine.square import indexToAlgebraic

PIECE_TO_SAN = {
    PieceType.KING: "K",
    PieceType.QUEEN: "Q",
    PieceType.ROOK: "R",
    PieceType.BISHOP: "B",
    PieceType.KNIGHT: "N",
    PieceType.PAWN: "",
}

PROMOTION_TO_SAN = {
    PieceType.QUEEN: "Q",
    PieceType.ROOK: "R",
    PieceType.BISHOP: "B",
    PieceType.KNIGHT: "N",
}

def findLegalMoveByUci(gameState, uci: str) -> Move | None:
    cleaned = (uci or "").strip().lower()
    for move in gameState.legalMoves():
        if move.basicUci() == cleaned:
            return move
    return None

def generateSanBeforeMove(gameState, move: Move) -> str:
    if move.isCastleKingside:
        base = "O-O"
    elif move.isCastleQueenside:
        base = "O-O-O"
    else:
        piece = move.movingPiece
        targetText = indexToAlgebraic(move.toSquare)
        capture = move.capturedPiece is not None or move.isEnPassant
        pieceLetter = PIECE_TO_SAN[piece.pieceType]
        disambiguation = ""
        if piece.pieceType != PieceType.PAWN:
            disambiguation = getDisambiguation(gameState, move)
        elif capture:
            disambiguation = indexToAlgebraic(move.fromSquare)[0]
        base = pieceLetter + disambiguation
        if capture:
            base += "x"
        base += targetText
        if move.promotionPieceType is not None:
            base += "=" + PROMOTION_TO_SAN[move.promotionPieceType]

    gameState.makeMove(move)
    status = gameState.status()
    gameState.undoMove()
    if status.value == "checkmate":
        base += "#"
    else:
        from engine.legality import isKingInCheck
        if isKingInCheckAfterMove(gameState, move):
            base += "+"
    return base

def isKingInCheckAfterMove(gameState, move: Move) -> bool:
    from engine.constants import opposite
    from engine.legality import isKingInCheck
    defender = opposite(gameState.sideToMove)
    gameState.makeMove(move)
    result = isKingInCheck(gameState, defender)
    gameState.undoMove()
    return result

def getDisambiguation(gameState, move: Move) -> str:
    sameTypeMoves = []
    for candidate in gameState.legalMoves():
        if candidate is move:
            continue
        if candidate.toSquare != move.toSquare:
            continue
        if candidate.fromSquare == move.fromSquare:
            continue
        if candidate.movingPiece.pieceType == move.movingPiece.pieceType and candidate.movingPiece.colour == move.movingPiece.colour:
            sameTypeMoves.append(candidate)
    if not sameTypeMoves:
        return ""
    fromAlg = indexToAlgebraic(move.fromSquare)
    sameFile = any(indexToAlgebraic(candidate.fromSquare)[0] == fromAlg[0] for candidate in sameTypeMoves)
    sameRank = any(indexToAlgebraic(candidate.fromSquare)[1] == fromAlg[1] for candidate in sameTypeMoves)
    if not sameFile:
        return fromAlg[0]
    if not sameRank:
        return fromAlg[1]
    return fromAlg
