# Chess NEA Project

A complete A-Level Computer Science NEA style chess application with a manually written chess engine, AI search and a Flask web interface.

## Main features

- Manual chess engine with FEN import/export
- Full legal move generation: check, checkmate, stalemate, castling, en passant and promotion
- Make/unmake move system for search and testing
- Perft testing harness
- AI opponent using negamax, alpha-beta pruning, quiescence search, move ordering and a transposition table
- Evaluation using material, piece-square tables, mobility, pawn structure and king safety
- PGN/SAN export support
- Flask app structure with game, analysis and puzzle routes
- JavaScript chessboard frontend with backend-authoritative move validation
- SQLite persistence through SQLAlchemy models
- Seed puzzle and opening data
- Automated tests for engine rules, special moves, search and optional Flask API

## Setup

Python 3.11+ is recommended.

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run tests

```bash
python -m pytest
```

The core engine tests do not require Flask. The API tests automatically skip if Flask/Flask-SQLAlchemy are not installed.

## Run the web app

```bash
python Server.py
```

Then open `http://127.0.0.1:5000`.

## Notes for NEA use

The engine deliberately does not use a chess library. Flask and SQLAlchemy are used only for routing and persistence. The source code is split so that the algorithmic chess logic can be tested independently from the web layer.
