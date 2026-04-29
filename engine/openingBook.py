import json
import random
from pathlib import Path
from engine.fen import exportFen, normaliseFenForRepetition
from engine.notation import findLegalMoveByUci

class OpeningBook:
    def __init__(self, bookPath: str | Path):
        self.bookPath = Path(bookPath)
        self.positions = self.loadBook(self.bookPath)

    def loadBook(self, bookPath: Path) -> dict[str, list[dict]]:
        if not bookPath.exists():
            return {}
        return json.loads(bookPath.read_text(encoding="utf-8"))

    def getBookMove(self, gameState):
        key = normaliseFenForRepetition(exportFen(gameState))
        options = self.positions.get(key)
        if not options:
            return None
        totalWeight = sum(item.get("weight", 1) for item in options)
        choice = random.randint(1, totalWeight)
        running = 0
        for item in options:
            running += item.get("weight", 1)
            if choice <= running:
                return findLegalMoveByUci(gameState, item["move"])
        return None
