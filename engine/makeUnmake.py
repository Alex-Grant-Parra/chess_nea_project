from dataclasses import dataclass
from engine.castlingRights import CastlingRights
from engine.constants import Colour, PieceType, opposite
from engine.move import Move
from engine.piece import Piece
from engine.square import algebraicToIndex

@dataclass
class MoveRecord:
    move: Move
    previousSquares: list[Piece | None]
    previousCastlingRights: CastlingRights
    previousEnPassantTarget: int | None
    previousHalfMoveClock: int
    previousFullMoveNumber: int
    previousSideToMove: Colour
    previousZobristHash: int
    previousPositionHashes: dict[int, int]

class MakeUnmake:
    @staticmethod
    def applyMove(gameState, move: Move) -> None:
        record = MoveRecord(
            move=move,
            previousSquares=gameState.board.squares.copy(),
            previousCastlingRights=gameState.castlingRights.clone(),
            previousEnPassantTarget=gameState.enPassantTarget,
            previousHalfMoveClock=gameState.halfMoveClock,
            previousFullMoveNumber=gameState.fullMoveNumber,
            previousSideToMove=gameState.sideToMove,
            previousZobristHash=gameState.zobristHash,
            previousPositionHashes=gameState.positionHashes.copy(),
        )
        gameState.moveHistory.append(record)

        movingPiece = gameState.board.getPiece(move.fromSquare)
        if movingPiece is None:
            raise ValueError("Cannot move from empty square")

        capturedPiece = move.capturedPiece
        isPawnMove = movingPiece.pieceType == PieceType.PAWN
        isCapture = capturedPiece is not None or move.isEnPassant

        gameState.enPassantTarget = None

        if move.isCastleKingside or move.isCastleQueenside:
            MakeUnmake.applyCastle(gameState, move, movingPiece)
        elif move.isEnPassant:
            MakeUnmake.applyEnPassant(gameState, move, movingPiece)
        else:
            gameState.board.setPiece(move.fromSquare, None)
            placedPiece = movingPiece.withMoved()
            if move.promotionPieceType is not None:
                placedPiece = Piece(move.promotionPieceType, movingPiece.colour, True, movingPiece.pieceId)
            gameState.board.setPiece(move.toSquare, placedPiece)

        if move.isDoublePawnPush:
            direction = 1 if movingPiece.colour == Colour.WHITE else -1
            gameState.enPassantTarget = move.fromSquare + (8 * direction)

        MakeUnmake.updateCastlingRights(gameState, move, movingPiece)

        gameState.halfMoveClock = 0 if isPawnMove or isCapture else gameState.halfMoveClock + 1
        if movingPiece.colour == Colour.BLACK:
            gameState.fullMoveNumber += 1
        gameState.sideToMove = opposite(gameState.sideToMove)
        gameState.refreshHash()
        gameState.positionHashes[gameState.zobristHash] = gameState.positionHashes.get(gameState.zobristHash, 0) + 1

    @staticmethod
    def applyCastle(gameState, move: Move, king: Piece) -> None:
        if king.colour == Colour.WHITE:
            if move.isCastleKingside:
                kingFrom, kingTo, rookFrom, rookTo = algebraicToIndex("e1"), algebraicToIndex("g1"), algebraicToIndex("h1"), algebraicToIndex("f1")
            else:
                kingFrom, kingTo, rookFrom, rookTo = algebraicToIndex("e1"), algebraicToIndex("c1"), algebraicToIndex("a1"), algebraicToIndex("d1")
        else:
            if move.isCastleKingside:
                kingFrom, kingTo, rookFrom, rookTo = algebraicToIndex("e8"), algebraicToIndex("g8"), algebraicToIndex("h8"), algebraicToIndex("f8")
            else:
                kingFrom, kingTo, rookFrom, rookTo = algebraicToIndex("e8"), algebraicToIndex("c8"), algebraicToIndex("a8"), algebraicToIndex("d8")
        rook = gameState.board.getPiece(rookFrom)
        gameState.board.setPiece(kingFrom, None)
        gameState.board.setPiece(rookFrom, None)
        gameState.board.setPiece(kingTo, king.withMoved())
        if rook is not None:
            gameState.board.setPiece(rookTo, rook.withMoved())

    @staticmethod
    def applyEnPassant(gameState, move: Move, pawn: Piece) -> None:
        direction = 1 if pawn.colour == Colour.WHITE else -1
        capturedSquare = move.toSquare - (8 * direction)
        gameState.board.setPiece(move.fromSquare, None)
        gameState.board.setPiece(capturedSquare, None)
        gameState.board.setPiece(move.toSquare, pawn.withMoved())

    @staticmethod
    def updateCastlingRights(gameState, move: Move, movingPiece: Piece) -> None:
        if movingPiece.pieceType == PieceType.KING:
            gameState.castlingRights.removeForColour(movingPiece.colour)
        elif movingPiece.pieceType == PieceType.ROOK:
            MakeUnmake.removeRookCastlingRight(gameState, move.fromSquare, movingPiece.colour)

        if move.capturedPiece is not None and move.capturedPiece.pieceType == PieceType.ROOK:
            MakeUnmake.removeRookCastlingRight(gameState, move.toSquare, move.capturedPiece.colour)

    @staticmethod
    def removeRookCastlingRight(gameState, squareIndex: int, colour: Colour) -> None:
        if colour == Colour.WHITE:
            if squareIndex == algebraicToIndex("h1"):
                gameState.castlingRights.removeKingside(Colour.WHITE)
            elif squareIndex == algebraicToIndex("a1"):
                gameState.castlingRights.removeQueenside(Colour.WHITE)
        else:
            if squareIndex == algebraicToIndex("h8"):
                gameState.castlingRights.removeKingside(Colour.BLACK)
            elif squareIndex == algebraicToIndex("a8"):
                gameState.castlingRights.removeQueenside(Colour.BLACK)

    @staticmethod
    def undoLastMove(gameState) -> None:
        if not gameState.moveHistory:
            raise ValueError("No move to undo")
        record = gameState.moveHistory.pop()
        gameState.board.squares = record.previousSquares
        gameState.castlingRights = record.previousCastlingRights
        gameState.enPassantTarget = record.previousEnPassantTarget
        gameState.halfMoveClock = record.previousHalfMoveClock
        gameState.fullMoveNumber = record.previousFullMoveNumber
        gameState.sideToMove = record.previousSideToMove
        gameState.zobristHash = record.previousZobristHash
        gameState.positionHashes = record.previousPositionHashes
