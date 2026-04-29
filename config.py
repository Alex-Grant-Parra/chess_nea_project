from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(exist_ok=True)

class Config:
    SECRET_KEY = "dev-secret-change-before-deployment"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{INSTANCE_DIR / 'chess.db'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AI_DEFAULT_TIME_LIMIT_SECONDS = 1.0
    AI_MAX_DEPTH = 5
    JSON_SORT_KEYS = False
