from datetime import datetime
from engine.notation import generateSanBeforeMove, findLegalMoveByUci

class PgnExporter:
    def exportFromUciMoves(self, startingGameState, uciMoves: list[str], tags: dict[str, str] | None = None) -> str:
        tags = tags or {}
        defaultTags = {
            "Event": "Chess NEA Game",
            "Site": "Local Flask App",
            "Date": datetime.now().strftime("%Y.%m.%d"),
            "White": "White",
            "Black": "Black",
            "Result": "*",
        }
        defaultTags.update(tags)
        lines = [f'[{key} "{value}"]' for key, value in defaultTags.items()]
        lines.append("")
        gameState = startingGameState
        moveTexts = []
        for index, uci in enumerate(uciMoves):
            move = findLegalMoveByUci(gameState, uci)
            if move is None:
                raise ValueError(f"Illegal PGN move in history: {uci}")
            if index % 2 == 0:
                moveTexts.append(f"{index // 2 + 1}.")
            san = generateSanBeforeMove(gameState, move)
            moveTexts.append(san)
            gameState.makeMove(move)
        moveTexts.append(defaultTags["Result"])
        lines.append(" ".join(moveTexts))
        return "\n".join(lines)
