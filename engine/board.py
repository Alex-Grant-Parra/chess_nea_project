from engine.constants import Colour, PieceType
from engine.piece import Piece
from engine.exceptions import InvalidBoardError

class Board:
    def __init__(self):
        self.squares: list[Piece | None] = [None] * 64

    def getPiece(self, squareIndex: int) -> Piece | None:
        return self.squares[squareIndex]

    def setPiece(self, squareIndex: int, piece: Piece | None) -> None:
        self.squares[squareIndex] = piece

    def movePiece(self, fromSquare: int, toSquare: int) -> Piece | None:
        capturedPiece = self.squares[toSquare]
        movingPiece = self.squares[fromSquare]
        self.squares[toSquare] = movingPiece.withMoved() if movingPiece is not None else None
        self.squares[fromSquare] = None
        return capturedPiece

    def clone(self) -> "Board":
        newBoard = Board()
        newBoard.squares = self.squares.copy()
        return newBoard

    def findKing(self, colour: Colour) -> int:
        for squareIndex, piece in enumerate(self.squares):
            if piece and piece.colour == colour and piece.pieceType == PieceType.KING:
                return squareIndex
        raise InvalidBoardError(f"{colour.value} king not found")

    def countPieces(self, pieceType: PieceType | None = None, colour: Colour | None = None) -> int:
        count = 0
        for piece in self.squares:
            if piece is None:
                continue
            if pieceType is not None and piece.pieceType != pieceType:
                continue
            if colour is not None and piece.colour != colour:
                continue
            count += 1
        return count

    def asFenPlacement(self) -> str:
        rows = []
        for rankIndex in range(7, -1, -1):
            emptyCount = 0
            row = ""
            for fileIndex in range(8):
                piece = self.squares[rankIndex * 8 + fileIndex]
                if piece is None:
                    emptyCount += 1
                else:
                    if emptyCount:
                        row += str(emptyCount)
                        emptyCount = 0
                    row += piece.fenSymbol()
            if emptyCount:
                row += str(emptyCount)
            rows.append(row)
        return "/".join(rows)
