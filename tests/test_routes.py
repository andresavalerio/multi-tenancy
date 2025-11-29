from fastapi.testclient import TestClient   

from src.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}

def test_read_admin():
    response = client.get("/api/admin")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello from admin"}

def test_read_public():
    response = client.get("/api/public")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello from public"}