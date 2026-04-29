from engine.constants import (
    BISHOP_DIRECTIONS,
    Colour,
    KING_OFFSETS,
    KNIGHT_OFFSETS,
    PROMOTION_PIECES,
    PieceType,
    QUEEN_DIRECTIONS,
    ROOK_DIRECTIONS,
    opposite,
)
from engine.legality import isKingInCheck, isSquareAttacked
from engine.move import Move
from engine.square import algebraicToIndex, isOnBoard, toCoords, toIndex

class MoveGenerator:
    def __init__(self, gameState):
        self.gameState = gameState

    def generateLegalMoves(self) -> list[Move]:
        movingColour = self.gameState.sideToMove
        pseudoLegalMoves = self.generatePseudoLegalMoves()
        legalMoves: list[Move] = []
        for move in pseudoLegalMoves:
            self.gameState.makeMove(move)
            if not isKingInCheck(self.gameState, movingColour):
                legalMoves.append(move)
            self.gameState.undoMove()
        return legalMoves

    def generatePseudoLegalMoves(self) -> list[Move]:
        moves: list[Move] = []
        for squareIndex in range(64):
            piece = self.gameState.board.getPiece(squareIndex)
            if piece is None or piece.colour != self.gameState.sideToMove:
                continue
            if piece.pieceType == PieceType.PAWN:
                moves.extend(self.generatePawnMoves(squareIndex, piece))
            elif piece.pieceType == PieceType.KNIGHT:
                moves.extend(self.generateKnightMoves(squareIndex, piece))
            elif piece.pieceType == PieceType.BISHOP:
                moves.extend(self.generateSlidingMoves(squareIndex, piece, BISHOP_DIRECTIONS))
            elif piece.pieceType == PieceType.ROOK:
                moves.extend(self.generateSlidingMoves(squareIndex, piece, ROOK_DIRECTIONS))
            elif piece.pieceType == PieceType.QUEEN:
                moves.extend(self.generateSlidingMoves(squareIndex, piece, QUEEN_DIRECTIONS))
            elif piece.pieceType == PieceType.KING:
                moves.extend(self.generateKingMoves(squareIndex, piece))
        return moves

    def generatePawnMoves(self, fromSquare: int, pawn) -> list[Move]:
        moves: list[Move] = []
        direction = 1 if pawn.colour == Colour.WHITE else -1
        startRank = 1 if pawn.colour == Colour.WHITE else 6
        promotionRank = 7 if pawn.colour == Colour.WHITE else 0
        fileIndex, rankIndex = toCoords(fromSquare)

        oneRank = rankIndex + direction
        if isOnBoard(fileIndex, oneRank):
            oneSquare = toIndex(fileIndex, oneRank)
            if self.gameState.board.getPiece(oneSquare) is None:
                self.addPawnMoveOrPromotions(moves, fromSquare, oneSquare, pawn, None, promotionRank)
                twoRank = rankIndex + direction * 2
                if rankIndex == startRank and isOnBoard(fileIndex, twoRank):
                    twoSquare = toIndex(fileIndex, twoRank)
                    if self.gameState.board.getPiece(twoSquare) is None:
                        moves.append(Move(fromSquare, twoSquare, pawn, isDoublePawnPush=True))

        for fileOffset in (-1, 1):
            targetFile = fileIndex + fileOffset
            targetRank = rankIndex + direction
            if not isOnBoard(targetFile, targetRank):
                continue
            targetSquare = toIndex(targetFile, targetRank)
            targetPiece = self.gameState.board.getPiece(targetSquare)
            if targetPiece is not None and targetPiece.colour != pawn.colour:
                self.addPawnMoveOrPromotions(moves, fromSquare, targetSquare, pawn, targetPiece, promotionRank)
            elif self.gameState.enPassantTarget == targetSquare:
                capturedSquare = targetSquare - (8 * direction)
                capturedPiece = self.gameState.board.getPiece(capturedSquare)
                moves.append(Move(fromSquare, targetSquare, pawn, capturedPiece=capturedPiece, isEnPassant=True))
        return moves

    def addPawnMoveOrPromotions(self, moves, fromSquare, toSquare, pawn, capturedPiece, promotionRank) -> None:
        _, targetRank = toCoords(toSquare)
        if targetRank == promotionRank:
            for promotionPieceType in PROMOTION_PIECES:
                moves.append(Move(fromSquare, toSquare, pawn, capturedPiece=capturedPiece, promotionPieceType=promotionPieceType))
        else:
            moves.append(Move(fromSquare, toSquare, pawn, capturedPiece=capturedPiece))

    def generateKnightMoves(self, fromSquare: int, knight) -> list[Move]:
        moves: list[Move] = []
        fileIndex, rankIndex = toCoords(fromSquare)
        for fileOffset, rankOffset in KNIGHT_OFFSETS:
            targetFile = fileIndex + fileOffset
            targetRank = rankIndex + rankOffset
            if not isOnBoard(targetFile, targetRank):
                continue
            targetSquare = toIndex(targetFile, targetRank)
            targetPiece = self.gameState.board.getPiece(targetSquare)
            if targetPiece is None or targetPiece.colour != knight.colour:
                moves.append(Move(fromSquare, targetSquare, knight, capturedPiece=targetPiece))
        return moves

    def generateSlidingMoves(self, fromSquare: int, piece, directions) -> list[Move]:
        moves: list[Move] = []
        fileIndex, rankIndex = toCoords(fromSquare)
        for fileStep, rankStep in directions:
            targetFile = fileIndex + fileStep
            targetRank = rankIndex + rankStep
            while isOnBoard(targetFile, targetRank):
                targetSquare = toIndex(targetFile, targetRank)
                targetPiece = self.gameState.board.getPiece(targetSquare)
                if targetPiece is None:
                    moves.append(Move(fromSquare, targetSquare, piece))
                else:
                    if targetPiece.colour != piece.colour:
                        moves.append(Move(fromSquare, targetSquare, piece, capturedPiece=targetPiece))
                    break
                targetFile += fileStep
                targetRank += rankStep
        return moves

    def generateKingMoves(self, fromSquare: int, king) -> list[Move]:
        moves: list[Move] = []
        fileIndex, rankIndex = toCoords(fromSquare)
        for fileOffset, rankOffset in KING_OFFSETS:
            targetFile = fileIndex + fileOffset
            targetRank = rankIndex + rankOffset
            if not isOnBoard(targetFile, targetRank):
                continue
            targetSquare = toIndex(targetFile, targetRank)
            targetPiece = self.gameState.board.getPiece(targetSquare)
            if targetPiece is None or targetPiece.colour != king.colour:
                moves.append(Move(fromSquare, targetSquare, king, capturedPiece=targetPiece))

        if not isKingInCheck(self.gameState, king.colour):
            if self.canCastleKingside(king.colour):
                target = algebraicToIndex("g1") if king.colour == Colour.WHITE else algebraicToIndex("g8")
                moves.append(Move(fromSquare, target, king, isCastleKingside=True))
            if self.canCastleQueenside(king.colour):
                target = algebraicToIndex("c1") if king.colour == Colour.WHITE else algebraicToIndex("c8")
                moves.append(Move(fromSquare, target, king, isCastleQueenside=True))
        return moves

    def canCastleKingside(self, colour: Colour) -> bool:
        if not self.gameState.castlingRights.canCastleKingside(colour):
            return False
        if colour == Colour.WHITE:
            kingSquare, rookSquare = algebraicToIndex("e1"), algebraicToIndex("h1")
            pathSquares = [algebraicToIndex("f1"), algebraicToIndex("g1")]
            safeSquares = [algebraicToIndex("f1"), algebraicToIndex("g1")]
        else:
            kingSquare, rookSquare = algebraicToIndex("e8"), algebraicToIndex("h8")
            pathSquares = [algebraicToIndex("f8"), algebraicToIndex("g8")]
            safeSquares = [algebraicToIndex("f8"), algebraicToIndex("g8")]
        return self.canCastleThrough(colour, kingSquare, rookSquare, pathSquares, safeSquares)

    def canCastleQueenside(self, colour: Colour) -> bool:
        if not self.gameState.castlingRights.canCastleQueenside(colour):
            return False
        if colour == Colour.WHITE:
            kingSquare, rookSquare = algebraicToIndex("e1"), algebraicToIndex("a1")
            pathSquares = [algebraicToIndex("d1"), algebraicToIndex("c1"), algebraicToIndex("b1")]
            safeSquares = [algebraicToIndex("d1"), algebraicToIndex("c1")]
        else:
            kingSquare, rookSquare = algebraicToIndex("e8"), algebraicToIndex("a8")
            pathSquares = [algebraicToIndex("d8"), algebraicToIndex("c8"), algebraicToIndex("b8")]
            safeSquares = [algebraicToIndex("d8"), algebraicToIndex("c8")]
        return self.canCastleThrough(colour, kingSquare, rookSquare, pathSquares, safeSquares)

    def canCastleThrough(self, colour: Colour, kingSquare: int, rookSquare: int, pathSquares: list[int], safeSquares: list[int]) -> bool:
        king = self.gameState.board.getPiece(kingSquare)
        rook = self.gameState.board.getPiece(rookSquare)
        if king is None or rook is None:
            return False
        if king.colour != colour or rook.colour != colour:
            return False
        if king.pieceType != PieceType.KING or rook.pieceType != PieceType.ROOK:
            return False
        for square in pathSquares:
            if self.gameState.board.getPiece(square) is not None:
                return False
        for square in safeSquares:
            if isSquareAttacked(self.gameState, square, opposite(colour)):
                return False
        return True
