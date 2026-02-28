from fastapi.testclient import TestClient
from app.main import app

# On crée un faux client web pour tester notre API
client = TestClient(app)

def test_health_check():
    """Vérifie que l'API démarre correctement et renvoie le statut OK"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "CliniQ API", "version": "1.0.0"}