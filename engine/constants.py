from enum import Enum

class Colour(Enum):
    WHITE = "white"
    BLACK = "black"

class PieceType(Enum):
    KING = "king"
    QUEEN = "queen"
    ROOK = "rook"
    BISHOP = "bishop"
    KNIGHT = "knight"
    PAWN = "pawn"

class GameStatus(Enum):
    ACTIVE = "active"
    CHECKMATE = "checkmate"
    STALEMATE = "stalemate"
    DRAW_FIFTY_MOVE = "draw_fifty_move"
    DRAW_THREEFOLD = "draw_threefold"
    DRAW_INSUFFICIENT = "draw_insufficient_material"
    RESIGNED = "resigned"
    TIMEOUT = "timeout"

BOARD_SIZE = 8
WHITE_BACK_RANK = 0
BLACK_BACK_RANK = 7
START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

INFINITY = 10_000_000
CHECKMATE_SCORE = 1_000_000
DRAW_SCORE = 0

PIECE_VALUES = {
    PieceType.PAWN: 100,
    PieceType.KNIGHT: 320,
    PieceType.BISHOP: 330,
    PieceType.ROOK: 500,
    PieceType.QUEEN: 900,
    PieceType.KING: 0,
}

KNIGHT_OFFSETS = [
    (1, 2), (2, 1), (2, -1), (1, -2),
    (-1, -2), (-2, -1), (-2, 1), (-1, 2),
]

KING_OFFSETS = [
    (1, 0), (1, 1), (0, 1), (-1, 1),
    (-1, 0), (-1, -1), (0, -1), (1, -1),
]

ROOK_DIRECTIONS = [(1, 0), (-1, 0), (0, 1), (0, -1)]
BISHOP_DIRECTIONS = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
QUEEN_DIRECTIONS = ROOK_DIRECTIONS + BISHOP_DIRECTIONS

PROMOTION_PIECES = [PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT]

def opposite(colour: Colour) -> Colour:
    return Colour.BLACK if colour == Colour.WHITE else Colour.WHITE
