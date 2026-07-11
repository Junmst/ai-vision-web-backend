import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers(client):
    username = f"api_test_{uuid.uuid4().hex[:12]}"
    password = "test-password-123"

    register_response = client.post(
        "/api/auth/register",
        json={"username": username, "password": password},
    )
    assert register_response.status_code == 200

    login_response = client.post(
        "/api/auth/login",
        data={"username": username, "password": password},
    )
    assert login_response.status_code == 200

    return {"Authorization": f"Bearer {login_response.json()['access_token']}"}


def test_root_reports_api_status(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "AI Vision Web API 运行中"


def test_authenticated_user_can_upload_and_access_image(client, auth_headers):
    upload_response = client.post(
        "/api/images",
        headers=auth_headers,
        files={"file": ("sample.png", b"test image bytes", "image/png")},
    )

    assert upload_response.status_code == 200
    image = upload_response.json()
    assert image["filename"] == "sample.png"
    assert image["url"].startswith("/uploads/")

    static_response = client.get(image["url"])
    assert static_response.status_code == 200
    assert static_response.content == b"test image bytes"

    list_response = client.get("/api/images", headers=auth_headers)
    assert list_response.status_code == 200
    assert any(item["id"] == image["id"] for item in list_response.json())

    delete_response = client.delete(f"/api/images/{image['id']}", headers=auth_headers)
    assert delete_response.status_code == 200


def test_upload_rejects_non_image_file(client, auth_headers):
    response = client.post(
        "/api/images",
        headers=auth_headers,
        files={"file": ("notes.txt", b"not an image", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "仅支持 JPG/PNG/GIF/WEBP 格式"


def test_authenticated_user_can_manage_ai_config(client, auth_headers):
    create_response = client.post(
        "/api/ai-configs",
        headers=auth_headers,
        json={
            "config_name": "test provider",
            "provider": "cloud",
            "base_url": "https://example.test/v1",
            "api_key": "not-a-real-secret",
            "model_name": "vision-model",
            "is_default": 1,
        },
    )

    assert create_response.status_code == 200
    schema = client.get("/openapi.json").json()
    create_schema = schema["components"]["schemas"]["AIConfigCreate"]
    assert "api_key" in create_schema["properties"]
    assert "api_key_encrypted" not in create_schema["properties"]

    config = create_response.json()
    assert "api_key_encrypted" not in config
    assert config["is_default"] == 1

    update_response = client.put(
        f"/api/ai-configs/{config['id']}",
        headers=auth_headers,
        json={"config_name": "updated provider", "is_default": 0},
    )
    assert update_response.status_code == 200
    assert update_response.json()["config_name"] == "updated provider"

    list_response = client.get("/api/ai-configs", headers=auth_headers)
    assert list_response.status_code == 200
    assert any(item["id"] == config["id"] for item in list_response.json())

    delete_response = client.delete(f"/api/ai-configs/{config['id']}", headers=auth_headers)
    assert delete_response.status_code == 200


def test_analysis_rejects_invalid_analysis_type(client, auth_headers):
    response = client.post(
        "/api/analysis",
        headers=auth_headers,
        json={"image_id": 999999, "analysis_type": "unsupported"},
    )

    assert response.status_code == 422


def test_analysis_rejects_missing_image_before_calling_ai(client, auth_headers):
    response = client.post(
        "/api/analysis",
        headers=auth_headers,
        json={"image_id": 999999, "analysis_type": "all"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "图片不存在"
