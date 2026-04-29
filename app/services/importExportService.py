from engine.fen import exportFen, loadFen
from engine.pgn import PgnExporter

class ImportExportService:
    def validateFen(self, fen: str) -> dict:
        try:
            gameState = loadFen(fen)
            return {"valid": True, "normalisedFen": exportFen(gameState)}
        except Exception as error:
            return {"valid": False, "error": str(error)}

    def exportPgnFromUci(self, startingFen: str, moves: list[str]) -> str:
        gameState = loadFen(startingFen)
        return PgnExporter().exportFromUciMoves(gameState, moves)

importExportService = ImportExportService()
