from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def createApp(configObject=Config):
    app = Flask(__name__)
    app.config.from_object(configObject)
    db.init_app(app)

    from app.routes.games import gamesBp
    from app.routes.analysis import analysisBp
    from app.routes.puzzles import puzzlesBp
    from app.routes.auth import authBp
    app.register_blueprint(gamesBp)
    app.register_blueprint(analysisBp)
    app.register_blueprint(puzzlesBp)
    app.register_blueprint(authBp)
    return app
