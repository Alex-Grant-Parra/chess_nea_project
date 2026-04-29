from dataclasses import dataclass
from engine.constants import PieceType, Colour

@dataclass(frozen=True)
class Piece:
    pieceType: PieceType
    colour: Colour
    hasMoved: bool = False
    pieceId: str | None = None

    def fenSymbol(self) -> str:
        symbols = {
            PieceType.KING: "k",
            PieceType.QUEEN: "q",
            PieceType.ROOK: "r",
            PieceType.BISHOP: "b",
            PieceType.KNIGHT: "n",
            PieceType.PAWN: "p",
        }
        symbol = symbols[self.pieceType]
        return symbol.upper() if self.colour == Colour.WHITE else symbol

    def withMoved(self) -> "Piece":
        return Piece(self.pieceType, self.colour, True, self.pieceId)
