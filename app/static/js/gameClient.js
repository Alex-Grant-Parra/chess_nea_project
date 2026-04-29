import { getJson, postJson } from "./api.js";
import { BoardRenderer } from "./boardRenderer.js";

const layout = document.querySelector(".game-layout");
const gameId = layout.dataset.gameId;
const boardRenderer = new BoardRenderer(document.getElementById("board"));
const statusText = document.getElementById("statusText");
const moveList = document.getElementById("moveList");
const fenBox = document.getElementById("fenBox");
let currentState = null;
let selectedSquare = null;
let legalTargets = [];
let legalMoves = [];

async function loadState() {
    currentState = await getJson(`/api/game/${gameId}/state`);
    legalMoves = currentState.legalMoves || [];
    render();
}

function render() {
    statusText.textContent = `${currentState.status} - ${currentState.sideToMove} to move`;
    fenBox.value = currentState.fen;
    moveList.innerHTML = "";
    for (const move of currentState.moveList) {
        const item = document.createElement("li");
        item.textContent = `${move.colour}: ${move.san} (${move.uci})`;
        moveList.appendChild(item);
    }
    boardRenderer.render(currentState.position, { selectedSquare, legalTargets });
}

async function onSquareClicked(squareIndex) {
    if (!currentState) return;
    if (selectedSquare === null) {
        const moves = await getJson(`/api/game/${gameId}/legal-moves?fromSquare=${squareIndex}`);
        if (moves.length === 0) return;
        selectedSquare = squareIndex;
        legalTargets = moves.map(move => move.toSquare);
        render();
        return;
    }
    if (legalTargets.includes(squareIndex)) {
        const matching = legalMoves.filter(uci => uci.startsWith(indexToSquare(selectedSquare) + indexToSquare(squareIndex)));
        let move = matching[0];
        if (matching.length > 1) {
            const promotion = prompt("Promote to q, r, b or n", "q") || "q";
            move = matching.find(uci => uci.endsWith(promotion.toLowerCase())) || matching[0];
        }
        try {
            currentState = await postJson(`/api/game/${gameId}/move`, { move });
        } catch (error) {
            alert(error.message);
            await loadState();
        }
    }
    selectedSquare = null;
    legalTargets = [];
    render();
}

function indexToSquare(squareIndex) {
    const file = "abcdefgh"[squareIndex % 8];
    const rank = Math.floor(squareIndex / 8) + 1;
    return file + rank;
}

boardRenderer.onSquareClicked = onSquareClicked;
document.getElementById("flipBoardButton").addEventListener("click", () => { boardRenderer.flip(); render(); });
loadState();
