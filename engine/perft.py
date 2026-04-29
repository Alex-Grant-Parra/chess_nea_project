def perft(gameState, depth: int) -> int:
    if depth == 0:
        return 1
    nodes = 0
    for move in gameState.legalMoves():
        gameState.makeMove(move)
        nodes += perft(gameState, depth - 1)
        gameState.undoMove()
    return nodes

def divide(gameState, depth: int) -> dict[str, int]:
    results = {}
    for move in gameState.legalMoves():
        gameState.makeMove(move)
        results[move.basicUci()] = perft(gameState, depth - 1)
        gameState.undoMove()
    return dict(sorted(results.items()))
