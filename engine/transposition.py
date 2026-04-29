from dataclasses import dataclass

EXACT = "EXACT"
LOWER_BOUND = "LOWER_BOUND"
UPPER_BOUND = "UPPER_BOUND"

@dataclass
class TranspositionEntry:
    zobristHash: int
    depth: int
    score: int
    flag: str
    bestMoveUci: str | None

class TranspositionTable:
    def __init__(self, maxEntries: int = 200_000):
        self.entries: dict[int, TranspositionEntry] = {}
        self.maxEntries = maxEntries
        self.hits = 0

    def lookup(self, zobristHash: int, depth: int, alpha: int, beta: int) -> int | None:
        entry = self.entries.get(zobristHash)
        if entry is None or entry.depth < depth:
            return None
        if entry.flag == EXACT:
            self.hits += 1
            return entry.score
        if entry.flag == LOWER_BOUND and entry.score >= beta:
            self.hits += 1
            return entry.score
        if entry.flag == UPPER_BOUND and entry.score <= alpha:
            self.hits += 1
            return entry.score
        return None

    def bestMoveUci(self, zobristHash: int) -> str | None:
        entry = self.entries.get(zobristHash)
        return entry.bestMoveUci if entry else None

    def store(self, zobristHash: int, depth: int, score: int, flag: str, bestMoveUci: str | None):
        if len(self.entries) >= self.maxEntries:
            self.entries.clear()
        self.entries[zobristHash] = TranspositionEntry(zobristHash, depth, score, flag, bestMoveUci)
