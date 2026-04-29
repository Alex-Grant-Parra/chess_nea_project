from engine.board import Board
from engine.castlingRights import CastlingRights
from engine.constants import Colour, GameStatus
from engine.repetition import positionKey

class GameState:
    def __init__(self, board: Board, sideToMove: Colour):
        self.board = board
        self.sideToMove = sideToMove
        self.castlingRights = CastlingRights.allAvailable()
        self.enPassantTarget: int | None = None
        self.halfMoveClock = 0
        self.fullMoveNumber = 1
        self.moveHistory = []
        self.positionHashes: dict[int, int] = {}
        self.zobristHash = 0
        self.refreshHash()

    def refreshHash(self) -> int:
        self.zobristHash = positionKey(self)
        return self.zobristHash

    def recordCurrentPosition(self) -> None:
        currentHash = self.refreshHash()
        self.positionHashes[currentHash] = self.positionHashes.get(currentHash, 0) + 1

    def legalMoves(self):
        from engine.moveGenerator import MoveGenerator
        return MoveGenerator(self).generateLegalMoves()

    def makeMove(self, move):
        from engine.makeUnmake import MakeUnmake
        MakeUnmake.applyMove(self, move)

    def undoMove(self):
        from engine.makeUnmake import MakeUnmake
        MakeUnmake.undoLastMove(self)

    def status(self) -> GameStatus:
        from engine.legality import isKingInCheck, hasInsufficientMaterial
        if self.halfMoveClock >= 100:
            return GameStatus.DRAW_FIFTY_MOVE
        if self.positionHashes.get(self.zobristHash, 0) >= 3:
            return GameStatus.DRAW_THREEFOLD
        if hasInsufficientMaterial(self):
            return GameStatus.DRAW_INSUFFICIENT
        legalMoves = self.legalMoves()
        if legalMoves:
            return GameStatus.ACTIVE
        if isKingInCheck(self, self.sideToMove):
            return GameStatus.CHECKMATE
        return GameStatus.STALEMATE
