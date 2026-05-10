from fastapi.testclient import TestClient
from api.main import app
import pytest

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome to TxGuard AI API" in response.json()["message"]

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

# Note: Testing scoring/ingestion would require a database.
# In a full test suite, we'd use a mock database or a test database.
