from dataclasses import dataclass
from engine.constants import Colour

@dataclass
class CastlingRights:
    whiteKingside: bool = False
    whiteQueenside: bool = False
    blackKingside: bool = False
    blackQueenside: bool = False

    @classmethod
    def allAvailable(cls) -> "CastlingRights":
        return cls(True, True, True, True)

    @classmethod
    def none(cls) -> "CastlingRights":
        return cls(False, False, False, False)

    @classmethod
    def fromFen(cls, text: str) -> "CastlingRights":
        if text == "-":
            return cls.none()
        allowed = set("KQkq")
        if any(char not in allowed for char in text):
            raise ValueError("Invalid castling rights")
        return cls("K" in text, "Q" in text, "k" in text, "q" in text)

    def clone(self) -> "CastlingRights":
        return CastlingRights(self.whiteKingside, self.whiteQueenside, self.blackKingside, self.blackQueenside)

    def toFen(self) -> str:
        text = ""
        if self.whiteKingside:
            text += "K"
        if self.whiteQueenside:
            text += "Q"
        if self.blackKingside:
            text += "k"
        if self.blackQueenside:
            text += "q"
        return text or "-"

    def canCastleKingside(self, colour: Colour) -> bool:
        return self.whiteKingside if colour == Colour.WHITE else self.blackKingside

    def canCastleQueenside(self, colour: Colour) -> bool:
        return self.whiteQueenside if colour == Colour.WHITE else self.blackQueenside

    def removeForColour(self, colour: Colour) -> None:
        if colour == Colour.WHITE:
            self.whiteKingside = False
            self.whiteQueenside = False
        else:
            self.blackKingside = False
            self.blackQueenside = False

    def removeKingside(self, colour: Colour) -> None:
        if colour == Colour.WHITE:
            self.whiteKingside = False
        else:
            self.blackKingside = False

    def removeQueenside(self, colour: Colour) -> None:
        if colour == Colour.WHITE:
            self.whiteQueenside = False
        else:
            self.blackQueenside = False
