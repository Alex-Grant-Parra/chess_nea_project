import pytest

flask = pytest.importorskip("flask")
pytest.importorskip("flask_sqlalchemy")

from app import createApp, db
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

@pytest.fixture()
def client():
    app = createApp(TestConfig)
    with app.app_context():
        db.create_all()
    with app.test_client() as client:
        yield client


def testCreateGameAndSubmitMove(client):
    response = client.post("/game/new", data={"mode": "local"}, follow_redirects=False)
    assert response.status_code == 302
    state = client.get("/api/game/1/state").get_json()
    assert state["status"] == "active"
    moveResponse = client.post("/api/game/1/move", json={"move": "e2e4"})
    assert moveResponse.status_code == 200
    assert moveResponse.get_json()["sideToMove"] == "black"


def testRejectIllegalMove(client):
    client.post("/game/new", data={"mode": "local"}, follow_redirects=False)
    response = client.post("/api/game/1/move", json={"move": "e2e5"})
    assert response.status_code == 400
