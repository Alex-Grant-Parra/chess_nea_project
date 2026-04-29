def toIndex(fileIndex: int, rankIndex: int) -> int:
    return rankIndex * 8 + fileIndex

def toCoords(squareIndex: int) -> tuple[int, int]:
    return squareIndex % 8, squareIndex // 8

def isOnBoard(fileIndex: int, rankIndex: int) -> bool:
    return 0 <= fileIndex < 8 and 0 <= rankIndex < 8

def algebraicToIndex(name: str) -> int:
    if len(name) != 2:
        raise ValueError(f"Invalid square name: {name}")
    fileIndex = ord(name[0].lower()) - ord("a")
    rankIndex = int(name[1]) - 1
    if not isOnBoard(fileIndex, rankIndex):
        raise ValueError(f"Square outside board: {name}")
    return toIndex(fileIndex, rankIndex)

def indexToAlgebraic(squareIndex: int) -> str:
    if not 0 <= squareIndex < 64:
        raise ValueError(f"Invalid square index: {squareIndex}")
    fileIndex, rankIndex = toCoords(squareIndex)
    return chr(ord("a") + fileIndex) + str(rankIndex + 1)

def squareColour(squareIndex: int) -> int:
    fileIndex, rankIndex = toCoords(squareIndex)
    return (fileIndex + rankIndex) % 2
