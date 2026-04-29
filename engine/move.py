from dataclasses import dataclass
from engine.piece import Piece
from engine.constants import PieceType
from engine.square import indexToAlgebraic

PROMOTION_TO_UCI = {
    PieceType.QUEEN: "q",
    PieceType.ROOK: "r",
    PieceType.BISHOP: "b",
    PieceType.KNIGHT: "n",
}

@dataclass
class Move:
    fromSquare: int
    toSquare: int
    movingPiece: Piece
    capturedPiece: Piece | None = None
    promotionPieceType: PieceType | None = None
    isCastleKingside: bool = False
    isCastleQueenside: bool = False
    isEnPassant: bool = False
    isDoublePawnPush: bool = False
    san: str | None = None

    def basicUci(self) -> str:
        text = indexToAlgebraic(self.fromSquare) + indexToAlgebraic(self.toSquare)
        if self.promotionPieceType is not None:
            text += PROMOTION_TO_UCI[self.promotionPieceType]
        return text

    def __hash__(self) -> int:
        return hash((self.fromSquare, self.toSquare, self.promotionPieceType))

    def matchesUci(self, uci: str) -> bool:
        return self.basicUci() == uci.lower()
