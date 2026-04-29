from datetime import datetime
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    passwordHash = db.Column(db.String(255), nullable=True)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    whiteUserId = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    blackUserId = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    mode = db.Column(db.String(30), nullable=False, default="local")
    startingFen = db.Column(db.Text, nullable=False)
    currentFen = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), nullable=False, default="active")
    result = db.Column(db.String(10), nullable=True)
    startedAt = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    endedAt = db.Column(db.DateTime, nullable=True)
    moves = db.relationship("MoveRecordDb", backref="game", lazy=True, cascade="all, delete-orphan")

class MoveRecordDb(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gameId = db.Column(db.Integer, db.ForeignKey("game.id"), nullable=False)
    moveNumber = db.Column(db.Integer, nullable=False)
    colour = db.Column(db.String(5), nullable=False)
    uci = db.Column(db.String(8), nullable=False)
    san = db.Column(db.String(20), nullable=False)
    fenAfterMove = db.Column(db.Text, nullable=False)
    timeRemainingMs = db.Column(db.Integer, nullable=True)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class AnalysisRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    fen = db.Column(db.Text, nullable=False)
    bestMove = db.Column(db.String(8), nullable=True)
    score = db.Column(db.Integer, nullable=True)
    depth = db.Column(db.Integer, nullable=True)
    pvLine = db.Column(db.Text, nullable=True)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class Puzzle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fen = db.Column(db.Text, nullable=False)
    solutionMoves = db.Column(db.Text, nullable=False)
    theme = db.Column(db.String(60), nullable=False)
    difficulty = db.Column(db.Integer, nullable=False, default=1)
    source = db.Column(db.String(120), nullable=True)

class PuzzleAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    puzzleId = db.Column(db.Integer, db.ForeignKey("puzzle.id"), nullable=False)
    userId = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    solved = db.Column(db.Boolean, default=False, nullable=False)
    attempts = db.Column(db.Integer, default=0, nullable=False)
    timeTakenSeconds = db.Column(db.Integer, nullable=True)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class OpeningBookMove(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    positionKey = db.Column(db.Text, nullable=False, index=True)
    uciMove = db.Column(db.String(8), nullable=False)
    weight = db.Column(db.Integer, default=1, nullable=False)
