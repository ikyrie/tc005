from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch


SERVICE_DIR = Path(__file__).resolve().parents[1]
if str(SERVICE_DIR) not in sys.path:
    sys.path.insert(0, str(SERVICE_DIR))

import ai_client  # noqa: E402


class TestAiClient_analyze_architecture:
    def test_deve_retornar_json_estruturado_quando_chamada_gemini_sucesso(self) -> None:
        expected_json = (
            '{"analysis_id":"11111111-1111-1111-1111-111111111111",'
            '"components":[],"risks":[],"recommendations":[],'
            '"limitations":[],"model":{"provider":"Google","model_name":"gemini-3.1-pro"}}'
        )

        with patch("ai_client.Image.open") as image_open_mock, patch("ai_client.genai.Client") as client_cls_mock:
            image_ctx = MagicMock()
            image_open_mock.return_value.__enter__.return_value = image_ctx

            client_instance = MagicMock()
            client_cls_mock.return_value = client_instance
            generate_content_mock = client_instance.models.generate_content
            generate_content_mock.return_value = SimpleNamespace(text=expected_json)

            result = ai_client.analyze_architecture("/tmp/page-1.png")

            assert result == expected_json
            generate_content_mock.assert_called_once()
