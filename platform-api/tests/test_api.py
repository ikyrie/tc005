from main import app
import sys
import os
from fastapi.testclient import TestClient

# Adiciona a pasta 'src' ao caminho de busca do Python para que o teste encontre o 'main'
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'src')))


client = TestClient(app)


def test_health_endpoint():
    """Garante que o endpoint de saúde responde estruturado."""
    response = client.get("/health")
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
    response = client.get(f"/v1/analyses/{fake_uuid}/status")
    assert response.status_code == 404
    assert response.json()["detail"] == "Análise não encontrada"


def test_get_analysis_report_not_found_while_processing():
    """Garante o critério de aceitação: Relatório responde 404 se não estiver pronto/registrado."""
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/v1/analyses/{fake_uuid}/report")
    assert response.status_code == 404


def test_upload_invalid_file_extension():
    """Valida se a API bloqueia extensões de arquivo não permitidas pelo edital."""
    files = {'file': ('executavel_suspeito.exe',
                      b'conteudo_binario_falso', 'application/octet-stream')}
    response = client.post("/v1/analyses", files=files)
    assert response.status_code == 400
    assert response.json()["detail"] == "Formato de arquivo não suportado"
