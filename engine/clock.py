from dataclasses import dataclass
from datetime import datetime
from engine.constants import Colour, opposite

@dataclass
class ChessClock:
    whiteMs: int
    blackMs: int
    incrementMs: int = 0
    activeColour: Colour | None = None
    lastTick: datetime | None = None

    def start(self, colour: Colour, now: datetime | None = None) -> None:
        self.activeColour = colour
        self.lastTick = now or datetime.utcnow()

    def applyMove(self, colour: Colour, now: datetime | None = None) -> None:
        now = now or datetime.utcnow()
        if self.lastTick is not None:
            elapsedMs = int((now - self.lastTick).total_seconds() * 1000)
            if colour == Colour.WHITE:
                self.whiteMs = max(0, self.whiteMs - elapsedMs + self.incrementMs)
            else:
                self.blackMs = max(0, self.blackMs - elapsedMs + self.incrementMs)
        self.activeColour = opposite(colour)
        self.lastTick = now

    def isTimedOut(self) -> bool:
        return self.whiteMs <= 0 or self.blackMs <= 0

    def serialise(self) -> dict:
        return {
            "whiteMs": self.whiteMs,
            "blackMs": self.blackMs,
            "incrementMs": self.incrementMs,
            "activeColour": self.activeColour.value if self.activeColour else None,
        }
