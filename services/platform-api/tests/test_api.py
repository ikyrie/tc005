from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import main as platform_main


class FakeDbSession:
    def add(self, _obj: object) -> None:
        return None

    def commit(self) -> None:
        return None

    def refresh(self, _obj: object) -> None:
        return None


@pytest.fixture
def client() -> TestClient:
    fake_db = FakeDbSession()

    def _override_get_db():
        yield fake_db

    platform_main.app.dependency_overrides[platform_main.get_db] = _override_get_db
    try:
        yield TestClient(platform_main.app)
    finally:
        platform_main.app.dependency_overrides.clear()


class TestUploadFile_upload_file:
    def test_deve_realizar_upload_de_diagrama_com_sucesso(self, client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(platform_main, "STORAGE_RAW_DIR", tmp_path / "raw")

        # Mock explícito do publicador para garantir isolamento de RabbitMQ.
        publisher_mock = Mock()
        monkeypatch.setattr(platform_main, "publish_analysis_requested", publisher_mock, raising=False)

        response = client.post(
            "/v1/analyses",
            files={"file": ("diagram.png", b"fake-image-content", "image/png")},
        )

        assert response.status_code == 201
        response_json = response.json()
        assert "analysis_id" in response_json
        assert response_json["status"] == "RECEIVED"


class TestResultCallback_internal_result:
    @pytest.mark.xfail(reason="Endpoint interno de callback de sucesso ainda nao implementado na API.")
    def test_deve_processar_callback_de_sucesso(self, client: TestClient) -> None:
        analysis_id = "6ec9dcf9-4df0-4e44-990e-294bf18eb8ff"
        payload = {
            "analysis_id": analysis_id,
            "components": [],
            "risks": [],
            "recommendations": [],
            "limitations": [],
            "model": {"provider": "Google", "model_name": "gemini-3.1-pro"},
        }

        response = client.post(f"/internal/v1/analyses/{analysis_id}/result", json=payload)

        assert response.status_code == 200


class TestErrorCallback_internal_error:
    @pytest.mark.xfail(reason="Endpoint interno de callback de erro ainda nao implementado na API.")
    def test_deve_processar_callback_de_erro(self, client: TestClient) -> None:
        analysis_id = "11111111-1111-1111-1111-111111111111"
        payload = {
            "error_code": "NORMALIZATION_FAILED",
            "error_message": "arquivo corrompido",
        }

        response = client.post(f"/internal/v1/analyses/{analysis_id}/error", json=payload)

        assert response.status_code == 200