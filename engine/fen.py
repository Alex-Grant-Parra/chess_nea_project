from engine.board import Board
from engine.castlingRights import CastlingRights
from engine.constants import START_FEN, Colour, PieceType
from engine.exceptions import FenError
from engine.gameState import GameState
from engine.piece import Piece
from engine.square import algebraicToIndex, indexToAlgebraic, toIndex

FEN_TO_PIECE = {
    "k": PieceType.KING,
    "q": PieceType.QUEEN,
    "r": PieceType.ROOK,
    "b": PieceType.BISHOP,
    "n": PieceType.KNIGHT,
    "p": PieceType.PAWN,
}

def loadFen(fenText: str = START_FEN) -> GameState:
    parts = fenText.strip().split()
    if len(parts) != 6:
        raise FenError("FEN must contain exactly 6 fields")

    piecePlacement, activeColour, castlingText, enPassantText, halfMoveText, fullMoveText = parts
    board = parsePiecePlacement(piecePlacement)
    sideToMove = parseActiveColour(activeColour)

    try:
        castlingRights = CastlingRights.fromFen(castlingText)
    except ValueError as error:
        raise FenError(str(error)) from error

    enPassantTarget = None if enPassantText == "-" else algebraicToIndex(enPassantText)

    try:
        halfMoveClock = int(halfMoveText)
        fullMoveNumber = int(fullMoveText)
    except ValueError as error:
        raise FenError("Halfmove and fullmove fields must be integers") from error

    if halfMoveClock < 0 or fullMoveNumber < 1:
        raise FenError("Invalid move counters")

    validateBoard(board)
    gameState = GameState(board, sideToMove)
    gameState.castlingRights = castlingRights
    gameState.enPassantTarget = enPassantTarget
    gameState.halfMoveClock = halfMoveClock
    gameState.fullMoveNumber = fullMoveNumber
    gameState.refreshHash()
    gameState.positionHashes = {gameState.zobristHash: 1}
    return gameState

def parsePiecePlacement(piecePlacement: str) -> Board:
    rows = piecePlacement.split("/")
    if len(rows) != 8:
        raise FenError("FEN piece placement must contain 8 ranks")
    board = Board()
    for fenRankIndex, row in enumerate(rows):
        rankIndex = 7 - fenRankIndex
        fileIndex = 0
        for char in row:
            if char.isdigit():
                fileIndex += int(char)
                continue
            lower = char.lower()
            if lower not in FEN_TO_PIECE:
                raise FenError(f"Invalid FEN piece symbol: {char}")
            if fileIndex >= 8:
                raise FenError("Too many squares in FEN rank")
            colour = Colour.WHITE if char.isupper() else Colour.BLACK
            board.setPiece(toIndex(fileIndex, rankIndex), Piece(FEN_TO_PIECE[lower], colour))
            fileIndex += 1
        if fileIndex != 8:
            raise FenError("Each FEN rank must contain 8 squares")
    return board

def parseActiveColour(activeColour: str) -> Colour:
    if activeColour == "w":
        return Colour.WHITE
    if activeColour == "b":
        return Colour.BLACK
    raise FenError("Active colour must be w or b")

def validateBoard(board: Board) -> None:
    whiteKings = board.countPieces(PieceType.KING, Colour.WHITE)
    blackKings = board.countPieces(PieceType.KING, Colour.BLACK)
    if whiteKings != 1 or blackKings != 1:
        raise FenError("Board must contain exactly one white king and one black king")
    for squareIndex, piece in enumerate(board.squares):
        if piece is not None and piece.pieceType == PieceType.PAWN:
            rankIndex = squareIndex // 8
            if rankIndex in (0, 7):
                raise FenError("Pawns cannot be on the first or eighth rank")

def exportFen(gameState: GameState) -> str:
    activeColour = "w" if gameState.sideToMove == Colour.WHITE else "b"
    castlingText = gameState.castlingRights.toFen()
    enPassantText = "-" if gameState.enPassantTarget is None else indexToAlgebraic(gameState.enPassantTarget)
    return f"{gameState.board.asFenPlacement()} {activeColour} {castlingText} {enPassantText} {gameState.halfMoveClock} {gameState.fullMoveNumber}"

def normaliseFenForRepetition(fenText: str) -> str:
    parts = fenText.split()
    return " ".join(parts[:4])
