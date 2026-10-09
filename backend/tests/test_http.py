from fastapi.testclient import TestClient

from app.main import app


def test_health_propagates_request_id():
    with TestClient(app) as client:
        response = client.get(
            "/health",
            headers={"X-Request-ID": "portfolio-test-request"},
        )

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.headers["X-Request-ID"] == "portfolio-test-request"
