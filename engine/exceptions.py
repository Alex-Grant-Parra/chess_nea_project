class ChessEngineError(Exception):
    pass

class InvalidMoveError(ChessEngineError):
    pass

class InvalidBoardError(ChessEngineError):
    pass

class FenError(ChessEngineError):
    pass

class PgnError(ChessEngineError):
    pass

class GameAlreadyFinishedError(ChessEngineError):
    pass

class SearchTimeout(ChessEngineError):
    pass
