from fastapi.testclient import TestClient

from app.main import app


def test_image_response_includes_public_url():
    schema = TestClient(app).get("/openapi.json").json()
    image_schema = schema["components"]["schemas"]["ImageOut"]

    assert "url" in image_schema["properties"]
    assert "url" in image_schema["required"]