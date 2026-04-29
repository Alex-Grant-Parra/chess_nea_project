const pieceGlyphs = {
    K: "♔", Q: "♕", R: "♖", B: "♗", N: "♘", P: "♙",
    k: "♚", q: "♛", r: "♜", b: "♝", n: "♞", p: "♟",
};

export class BoardRenderer {
    constructor(boardElement) {
        this.boardElement = boardElement;
        this.isFlipped = false;
        this.onSquareClicked = null;
    }

    render(position, options = {}) {
        this.boardElement.innerHTML = "";
        const order = this.squareOrder();
        for (const squareIndex of order) {
            const squareElement = document.createElement("div");
            squareElement.classList.add("square");
            squareElement.classList.add(this.isLight(squareIndex) ? "light" : "dark");
            squareElement.dataset.square = squareIndex;
            if (options.selectedSquare === squareIndex) squareElement.classList.add("selected");
            if ((options.legalTargets || []).includes(squareIndex)) squareElement.classList.add("legal");
            if ((options.lastMoveSquares || []).includes(squareIndex)) squareElement.classList.add("last");
            const piece = position[squareIndex];
            if (piece) {
                const pieceElement = document.createElement("span");
                pieceElement.classList.add("piece");
                pieceElement.textContent = pieceGlyphs[piece] || piece;
                squareElement.appendChild(pieceElement);
            }
            squareElement.addEventListener("click", () => this.onSquareClicked?.(squareIndex));
            this.boardElement.appendChild(squareElement);
        }
    }

    squareOrder() {
        const squares = [];
        const ranks = this.isFlipped ? [...Array(8).keys()] : [...Array(8).keys()].reverse();
        const files = this.isFlipped ? [...Array(8).keys()].reverse() : [...Array(8).keys()];
        for (const rank of ranks) for (const file of files) squares.push(rank * 8 + file);
        return squares;
    }

    isLight(squareIndex) {
        const file = squareIndex % 8;
        const rank = Math.floor(squareIndex / 8);
        return (file + rank) % 2 === 1;
    }

    flip() { this.isFlipped = !this.isFlipped; }
}
