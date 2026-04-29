import time
from dataclasses import dataclass
from engine.constants import CHECKMATE_SCORE, INFINITY, PIECE_VALUES
from engine.evaluation import Evaluator
from engine.exceptions import SearchTimeout
from engine.legality import isKingInCheck
from engine.move import Move
from engine.transposition import EXACT, LOWER_BOUND, UPPER_BOUND, TranspositionTable

@dataclass
class SearchResult:
    bestMove: Move | None
    score: int
    depthReached: int
    nodeCount: int
    elapsedMs: int
    principalVariation: list[str]
    transpositionHits: int

class Searcher:
    def __init__(self, evaluator: Evaluator | None = None):
        self.evaluator = evaluator or Evaluator()
        self.transpositionTable = TranspositionTable()
        self.nodeCount = 0
        self.startTime = 0.0
        self.timeLimitSeconds = 1.0
        self.rootBestMove: Move | None = None
        self.killerMoves: dict[int, list[str]] = {}
        self.historyScores: dict[str, int] = {}

    def findBestMove(self, gameState, timeLimitSeconds: float = 1.0, maxDepth: int = 5) -> SearchResult:
        self.startTime = time.perf_counter()
        self.timeLimitSeconds = timeLimitSeconds
        self.nodeCount = 0
        bestMove = None
        bestScore = -INFINITY
        depthReached = 0
        principalVariation: list[str] = []

        legalMoves = gameState.legalMoves()
        if not legalMoves:
            return SearchResult(None, 0, 0, 0, 0, [], self.transpositionTable.hits)

        for depth in range(1, maxDepth + 1):
            try:
                score, move = self.searchRoot(gameState, depth)
                if move is not None:
                    bestMove = move
                    bestScore = score
                    self.rootBestMove = move
                    depthReached = depth
                    principalVariation = self.extractPrincipalVariation(gameState, depth)
            except SearchTimeout:
                break
        elapsedMs = int((time.perf_counter() - self.startTime) * 1000)
        return SearchResult(bestMove, bestScore, depthReached, self.nodeCount, elapsedMs, principalVariation, self.transpositionTable.hits)

    def searchRoot(self, gameState, depth: int) -> tuple[int, Move | None]:
        alpha = -INFINITY
        beta = INFINITY
        bestScore = -INFINITY
        bestMove = None
        moves = self.orderMoves(gameState, gameState.legalMoves(), depth, 0)
        for move in moves:
            self.checkTimeout()
            gameState.makeMove(move)
            score = -self.negamax(gameState, depth - 1, -beta, -alpha, 1)
            gameState.undoMove()
            if score > bestScore:
                bestScore = score
                bestMove = move
            alpha = max(alpha, score)
        if bestMove is not None:
            self.transpositionTable.store(gameState.zobristHash, depth, bestScore, EXACT, bestMove.basicUci())
        return bestScore, bestMove

    def negamax(self, gameState, depth: int, alpha: int, beta: int, ply: int) -> int:
        self.checkTimeout()
        self.nodeCount += 1
        alphaOriginal = alpha

        lookupScore = self.transpositionTable.lookup(gameState.zobristHash, depth, alpha, beta)
        if lookupScore is not None:
            return lookupScore

        if depth <= 0:
            return self.quiescenceSearch(gameState, alpha, beta, ply)

        moves = gameState.legalMoves()
        if not moves:
            if isKingInCheck(gameState, gameState.sideToMove):
                return -CHECKMATE_SCORE + ply
            return 0

        bestScore = -INFINITY
        bestMove = None
        orderedMoves = self.orderMoves(gameState, moves, depth, ply)
        for move in orderedMoves:
            gameState.makeMove(move)
            score = -self.negamax(gameState, depth - 1, -beta, -alpha, ply + 1)
            gameState.undoMove()
            if score > bestScore:
                bestScore = score
                bestMove = move
            alpha = max(alpha, score)
            if alpha >= beta:
                if move.capturedPiece is None:
                    self.addKillerMove(ply, move.basicUci())
                    self.historyScores[move.basicUci()] = self.historyScores.get(move.basicUci(), 0) + depth * depth
                break

        if bestScore <= alphaOriginal:
            flag = UPPER_BOUND
        elif bestScore >= beta:
            flag = LOWER_BOUND
        else:
            flag = EXACT
        self.transpositionTable.store(gameState.zobristHash, depth, bestScore, flag, bestMove.basicUci() if bestMove else None)
        return bestScore

    def quiescenceSearch(self, gameState, alpha: int, beta: int, ply: int) -> int:
        self.checkTimeout()
        self.nodeCount += 1
        standPat = self.evaluator.evaluate(gameState)
        if standPat >= beta:
            return beta
        if alpha < standPat:
            alpha = standPat
        captureMoves = [move for move in gameState.legalMoves() if move.capturedPiece is not None or move.promotionPieceType is not None]
        for move in self.orderMoves(gameState, captureMoves, 0, ply):
            gameState.makeMove(move)
            score = -self.quiescenceSearch(gameState, -beta, -alpha, ply + 1)
            gameState.undoMove()
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
        return alpha

    def orderMoves(self, gameState, moves: list[Move], depth: int, ply: int) -> list[Move]:
        ttMove = self.transpositionTable.bestMoveUci(gameState.zobristHash)
        killerSet = set(self.killerMoves.get(ply, []))
        def scoreMove(move: Move) -> int:
            uci = move.basicUci()
            score = 0
            if self.rootBestMove is not None and uci == self.rootBestMove.basicUci():
                score += 2_000_000
            if ttMove and uci == ttMove:
                score += 1_500_000
            if move.capturedPiece is not None:
                victim = PIECE_VALUES[move.capturedPiece.pieceType]
                attacker = PIECE_VALUES[move.movingPiece.pieceType]
                score += 100_000 + victim * 10 - attacker
            if move.promotionPieceType is not None:
                score += 80_000 + PIECE_VALUES[move.promotionPieceType]
            if uci in killerSet:
                score += 50_000
            score += self.historyScores.get(uci, 0)
            return score
        return sorted(moves, key=scoreMove, reverse=True)

    def addKillerMove(self, ply: int, uci: str) -> None:
        moves = self.killerMoves.setdefault(ply, [])
        if uci not in moves:
            moves.insert(0, uci)
        del moves[2:]

    def extractPrincipalVariation(self, gameState, depth: int) -> list[str]:
        pv = []
        made = 0
        try:
            for _ in range(depth):
                uci = self.transpositionTable.bestMoveUci(gameState.zobristHash)
                if not uci:
                    break
                move = next((m for m in gameState.legalMoves() if m.basicUci() == uci), None)
                if move is None:
                    break
                pv.append(uci)
                gameState.makeMove(move)
                made += 1
        finally:
            for _ in range(made):
                gameState.undoMove()
        return pv

    def checkTimeout(self) -> None:
        if time.perf_counter() - self.startTime > self.timeLimitSeconds:
            raise SearchTimeout()
