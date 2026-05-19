from __future__ import annotations
import sys
from pathlib import Path

API_SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(API_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(API_SRC_DIR))

import main as platform_main
from main import app

import pytest


from unittest.mock import Mock

from fastapi.testclient import TestClient

clientNew = TestClient(app)


def test_health_endpoint():
    """Garante que o endpoint de saúde responde estruturado."""
    response = clientNew.get("/health")
    # Se a infra (Docker) estiver ligada, deve responder 200. Caso contrário, 503.
    assert response.status_code in [200, 503]

    if response.status_code == 200:
        data = response.json()
        assert data["status"] == "UP"
        assert "postgres" in data["services"]
        assert "rabbitmq" in data["services"]


def test_get_analysis_status_not_found():
    """Valida se buscar uma análise inexistente retorna corretamente o erro 404."""
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    response = clientNew.get(f"/v1/analyses/{fake_uuid}/status")
    assert response.status_code == 404
    assert response.json()["detail"] == "Análise não encontrada"


def test_get_analysis_report_not_found_while_processing():
    """Garante o critério de aceitação: Relatório responde 404 se não estiver pronto/registrado."""
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    response = clientNew.get(f"/v1/analyses/{fake_uuid}/report")
    assert response.status_code == 404


def test_upload_invalid_file_extension():
    """Valida se a API bloqueia extensões de arquivo não permitidas pelo edital."""
    files = {'file': ('executavel_suspeito.exe',
                      b'conteudo_binario_falso', 'application/octet-stream')}
    response = clientNew.post("/v1/analyses", files=files)
    assert response.status_code == 400
    assert response.json()["detail"] == "Formato de arquivo não suportado"


class FakeDbSession:
    def add(self, _obj: object) -> None:
        """Simula a inclusão de um objeto na sessão sem persistência real.

        Args:
            _obj (object): Objeto recebido para inclusão na sessão.

        Returns:
            None: Não retorna valor.
        """
        return None

    def commit(self) -> None:
        """Simula o commit da sessão sem efetuar gravação real.

        Returns:
            None: Não retorna valor.
        """
        return None

    def refresh(self, _obj: object) -> None:
        """Simula a atualização do objeto após o commit.

        Args:
            _obj (object): Objeto a ser atualizado em memória.

        Returns:
            None: Não retorna valor.
        """
        return None


@pytest.fixture
def client() -> TestClient:
    """Cria um cliente de teste com a dependência de banco substituída.

    Returns:
        TestClient: Cliente HTTP de teste configurado para a aplicação FastAPI.
    """
    fake_db = FakeDbSession()

    def _override_get_db():
        """Fornece a sessão fake usada durante os testes.

        Returns:
            Generator[FakeDbSession, None, None]: Gerador que entrega a sessão simulada.
        """
        yield fake_db

    platform_main.app.dependency_overrides[platform_main.get_db] = _override_get_db
    try:
        yield TestClient(platform_main.app)
    finally:
        platform_main.app.dependency_overrides.clear()


class TestUploadFile_upload_file:
    def test_deve_realizar_upload_de_diagrama_com_sucesso(
            self, client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Verifica se o upload cria a análise e marca o status como processamento.

        Args:
            client (TestClient): Cliente HTTP de teste com dependências sobrescritas.
            tmp_path (Path): Diretório temporário fornecido pelo pytest.
            monkeypatch (pytest.MonkeyPatch): Utilitário para substituir dependências.

        Returns:
            None: Não retorna valor.
        """
        monkeypatch.setattr(platform_main, "STORAGE_RAW_DIR", tmp_path / "raw")

        # Mock explícito do publicador para garantir isolamento de RabbitMQ.
        publisher_mock = Mock()
        monkeypatch.setattr(
            platform_main, "publish_analysis_requested", publisher_mock, raising=False)

        response = client.post(
            "/v1/analyses",
            files={
                "file": ("diagram.png", b"fake-image-content", "image/png")},
        )

        assert response.status_code == 201
        response_json = response.json()
        assert "analysis_id" in response_json
        assert response_json["status"] == "PROCESSING"


class TestResultCallback_internal_result:
    @pytest.mark.xfail(reason="Endpoint interno de callback de sucesso ainda nao implementado na API.")
    def test_deve_processar_callback_de_sucesso(self, client: TestClient) -> None:
        """Documenta o contrato esperado para o callback interno de sucesso.

        Args:
            client (TestClient): Cliente HTTP de teste com dependências sobrescritas.

        Returns:
            None: Não retorna valor.
        """
        analysis_id = "6ec9dcf9-4df0-4e44-990e-294bf18eb8ff"
        payload = {
            "analysis_id": analysis_id,
            "components": [],
            "risks": [],
            "recommendations": [],
            "limitations": [],
            "model": {"provider": "Google", "model_name": "gemini-3.1-pro"},
        }

        response = client.post(
            f"/internal/v1/analyses/{analysis_id}/result", json=payload)

        assert response.status_code == 200


class TestErrorCallback_internal_error:
    @pytest.mark.xfail(reason="Endpoint interno de callback de erro ainda nao implementado na API.")
    def test_deve_processar_callback_de_erro(self, client: TestClient) -> None:
        """Documenta o contrato esperado para o callback interno de erro.

        Args:
            client (TestClient): Cliente HTTP de teste com dependências sobrescritas.

        Returns:
            None: Não retorna valor.
        """
        analysis_id = "11111111-1111-1111-1111-111111111111"
        payload = {
            "error_code": "NORMALIZATION_FAILED",
            "error_message": "arquivo corrompido",
        }

        response = client.post(
            f"/internal/v1/analyses/{analysis_id}/error", json=payload)

        assert response.status_code == 200
