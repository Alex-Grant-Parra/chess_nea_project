import random
from engine.constants import Colour, PieceType

class ZobristHasher:
    def __init__(self):
        rng = random.Random(64_000_001)
        self.pieceKeys: dict[tuple[Colour, PieceType, int], int] = {}
        for colour in Colour:
            for pieceType in PieceType:
                for squareIndex in range(64):
                    self.pieceKeys[(colour, pieceType, squareIndex)] = rng.getrandbits(64)
        self.sideKey = rng.getrandbits(64)
        self.castlingKeys = {
            "K": rng.getrandbits(64),
            "Q": rng.getrandbits(64),
            "k": rng.getrandbits(64),
            "q": rng.getrandbits(64),
        }
        self.enPassantFileKeys = [rng.getrandbits(64) for _ in range(8)]

    def hashState(self, gameState) -> int:
        value = 0
        for squareIndex, piece in enumerate(gameState.board.squares):
            if piece is not None:
                value ^= self.pieceKeys[(piece.colour, piece.pieceType, squareIndex)]
        if gameState.sideToMove == Colour.BLACK:
            value ^= self.sideKey
        castlingText = gameState.castlingRights.toFen()
        if castlingText != "-":
            for char in castlingText:
                value ^= self.castlingKeys[char]
        if gameState.enPassantTarget is not None:
            value ^= self.enPassantFileKeys[gameState.enPassantTarget % 8]
        return value

zobristHasher = ZobristHasher()

def positionKey(gameState) -> int:
    return zobristHasher.hashState(gameState)
