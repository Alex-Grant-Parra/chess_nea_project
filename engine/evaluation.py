from engine.constants import Colour, GameStatus, PIECE_VALUES, PieceType, opposite
from engine.legality import isKingInCheck
from engine.square import toCoords

# Values are from White's perspective. Black uses the mirrored rank.
PAWN_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
     5,  5, 10, 25, 25, 10,  5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5, -5,-10,  0,  0,-10, -5,  5,
     5, 10, 10,-20,-20, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0,
]
KNIGHT_TABLE = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50,
]
BISHOP_TABLE = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -20,-10,-10,-10,-10,-10,-10,-20,
]
ROOK_TABLE = [
     0,  0,  0,  5,  5,  0,  0,  0,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
     5, 10, 10, 10, 10, 10, 10,  5,
     0,  0,  0,  5,  5,  0,  0,  0,
]
QUEEN_TABLE = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
     -5,  0,  5,  5,  5,  5,  0, -5,
      0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20,
]
KING_MIDDLE_TABLE = [
     20, 30, 10,  0,  0, 10, 30, 20,
     20, 20,  0,  0,  0,  0, 20, 20,
    -10,-20,-20,-20,-20,-20,-20,-10,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
]
PIECE_TABLES = {
    PieceType.PAWN: PAWN_TABLE,
    PieceType.KNIGHT: KNIGHT_TABLE,
    PieceType.BISHOP: BISHOP_TABLE,
    PieceType.ROOK: ROOK_TABLE,
    PieceType.QUEEN: QUEEN_TABLE,
    PieceType.KING: KING_MIDDLE_TABLE,
}

class Evaluator:
    def evaluate(self, gameState) -> int:
        score = 0
        score += self.materialAndPositionScore(gameState)
        score += self.bishopPairScore(gameState)
        score += self.pawnStructureScore(gameState)
        score += self.kingSafetyScore(gameState)
        score += self.mobilityScore(gameState)
        return score if gameState.sideToMove == Colour.WHITE else -score

    def materialAndPositionScore(self, gameState) -> int:
        score = 0
        for squareIndex, piece in enumerate(gameState.board.squares):
            if piece is None:
                continue
            sign = 1 if piece.colour == Colour.WHITE else -1
            score += sign * PIECE_VALUES[piece.pieceType]
            table = PIECE_TABLES[piece.pieceType]
            tableIndex = squareIndex if piece.colour == Colour.WHITE else mirrorSquare(squareIndex)
            score += sign * table[tableIndex]
        return score

    def bishopPairScore(self, gameState) -> int:
        score = 0
        for colour in (Colour.WHITE, Colour.BLACK):
            count = gameState.board.countPieces(PieceType.BISHOP, colour)
            if count >= 2:
                score += 35 if colour == Colour.WHITE else -35
        return score

    def pawnStructureScore(self, gameState) -> int:
        score = 0
        for colour in (Colour.WHITE, Colour.BLACK):
            fileCounts = [0] * 8
            pawnSquares = []
            for squareIndex, piece in enumerate(gameState.board.squares):
                if piece and piece.colour == colour and piece.pieceType == PieceType.PAWN:
                    fileIndex, rankIndex = toCoords(squareIndex)
                    fileCounts[fileIndex] += 1
                    pawnSquares.append((fileIndex, rankIndex, squareIndex))
            penalty = 0
            for count in fileCounts:
                if count > 1:
                    penalty += 12 * (count - 1)
            for fileIndex, _, _ in pawnSquares:
                left = fileCounts[fileIndex - 1] if fileIndex > 0 else 0
                right = fileCounts[fileIndex + 1] if fileIndex < 7 else 0
                if left == 0 and right == 0:
                    penalty += 10
            score += -penalty if colour == Colour.WHITE else penalty
        return score

    def kingSafetyScore(self, gameState) -> int:
        score = 0
        for colour in (Colour.WHITE, Colour.BLACK):
            try:
                kingSquare = gameState.board.findKing(colour)
            except Exception:
                continue
            fileIndex, rankIndex = toCoords(kingSquare)
            shieldRank = rankIndex + (1 if colour == Colour.WHITE else -1)
            shield = 0
            for fileOffset in (-1, 0, 1):
                fileToCheck = fileIndex + fileOffset
                if 0 <= fileToCheck < 8 and 0 <= shieldRank < 8:
                    piece = gameState.board.getPiece(shieldRank * 8 + fileToCheck)
                    if piece and piece.colour == colour and piece.pieceType == PieceType.PAWN:
                        shield += 1
            bonus = shield * 8
            score += bonus if colour == Colour.WHITE else -bonus
        return score

    def mobilityScore(self, gameState) -> int:
        # Cheap pseudo-mobility: legal move count from current side and opponent after a null-like toggle.
        try:
            own = len(gameState.legalMoves())
            gameState.sideToMove = opposite(gameState.sideToMove)
            opp = len(gameState.legalMoves())
            gameState.sideToMove = opposite(gameState.sideToMove)
            mobility = (own - opp) * 2
            return mobility if gameState.sideToMove == Colour.WHITE else -mobility
        except Exception:
            return 0

def mirrorSquare(squareIndex: int) -> int:
    fileIndex, rankIndex = toCoords(squareIndex)
    return (7 - rankIndex) * 8 + fileIndex
