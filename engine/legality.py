from engine.constants import (
    BISHOP_DIRECTIONS,
    Colour,
    KING_OFFSETS,
    KNIGHT_OFFSETS,
    PieceType,
    QUEEN_DIRECTIONS,
    ROOK_DIRECTIONS,
    opposite,
)
from engine.square import isOnBoard, toCoords, toIndex, squareColour


def isSquareAttacked(gameState, squareIndex: int, byColour: Colour) -> bool:
    board = gameState.board
    fileIndex, rankIndex = toCoords(squareIndex)

    # Pawn attacks: work backwards from the attacked square to possible pawn locations.
    pawnDirection = 1 if byColour == Colour.WHITE else -1
    pawnRank = rankIndex - pawnDirection
    for fileOffset in (-1, 1):
        pawnFile = fileIndex - fileOffset
        if isOnBoard(pawnFile, pawnRank):
            piece = board.getPiece(toIndex(pawnFile, pawnRank))
            if piece and piece.colour == byColour and piece.pieceType == PieceType.PAWN:
                return True

    for fileOffset, rankOffset in KNIGHT_OFFSETS:
        targetFile = fileIndex + fileOffset
        targetRank = rankIndex + rankOffset
        if isOnBoard(targetFile, targetRank):
            piece = board.getPiece(toIndex(targetFile, targetRank))
            if piece and piece.colour == byColour and piece.pieceType == PieceType.KNIGHT:
                return True

    for fileOffset, rankOffset in KING_OFFSETS:
        targetFile = fileIndex + fileOffset
        targetRank = rankIndex + rankOffset
        if isOnBoard(targetFile, targetRank):
            piece = board.getPiece(toIndex(targetFile, targetRank))
            if piece and piece.colour == byColour and piece.pieceType == PieceType.KING:
                return True

    for fileStep, rankStep in ROOK_DIRECTIONS:
        if rayContainsAttacker(gameState, fileIndex, rankIndex, fileStep, rankStep, byColour, {PieceType.ROOK, PieceType.QUEEN}):
            return True

    for fileStep, rankStep in BISHOP_DIRECTIONS:
        if rayContainsAttacker(gameState, fileIndex, rankIndex, fileStep, rankStep, byColour, {PieceType.BISHOP, PieceType.QUEEN}):
            return True

    return False


def rayContainsAttacker(gameState, fileIndex: int, rankIndex: int, fileStep: int, rankStep: int, byColour: Colour, attackers: set[PieceType]) -> bool:
    targetFile = fileIndex + fileStep
    targetRank = rankIndex + rankStep
    while isOnBoard(targetFile, targetRank):
        piece = gameState.board.getPiece(toIndex(targetFile, targetRank))
        if piece is not None:
            return piece.colour == byColour and piece.pieceType in attackers
        targetFile += fileStep
        targetRank += rankStep
    return False


def isKingInCheck(gameState, colour: Colour) -> bool:
    kingSquare = gameState.board.findKing(colour)
    return isSquareAttacked(gameState, kingSquare, opposite(colour))


def hasInsufficientMaterial(gameState) -> bool:
    pieces = [(i, p) for i, p in enumerate(gameState.board.squares) if p is not None]
    nonKings = [(i, p) for i, p in pieces if p.pieceType != PieceType.KING]
    if not nonKings:
        return True
    if len(nonKings) == 1 and nonKings[0][1].pieceType in (PieceType.BISHOP, PieceType.KNIGHT):
        return True
    if len(nonKings) == 2 and all(p.pieceType == PieceType.BISHOP for _, p in nonKings):
        return squareColour(nonKings[0][0]) == squareColour(nonKings[1][0])
    return False
