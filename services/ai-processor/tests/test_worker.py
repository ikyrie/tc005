from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock, patch


SERVICE_DIR = Path(__file__).resolve().parents[1]
if str(SERVICE_DIR) not in sys.path:
    sys.path.insert(0, str(SERVICE_DIR))

import worker


class TestWorker_on_message:
    def test_deve_processar_fluxo_de_sucesso_e_enviar_callback_de_resultado(self) -> None:
        channel = Mock()
        method = SimpleNamespace(delivery_tag="tag-1")
        body = b'{"analysis_id": "a-1", "object_key": "raw/a-1/original.png"}'
        result_json = json.dumps(
            {
                "analysis_id": "a-1",
                "components": [],
                "risks": [],
                "recommendations": [],
                "limitations": [],
                "model": {"provider": "Google", "model_name": "gemini-3.1-pro"},
            }
        )

        with patch("worker._process_message", return_value=("a-1", "raw/a-1/original.png", "/tmp/page-1.png")), patch(
            "worker.analyze_architecture", return_value=result_json
        ), patch("worker.httpx.Client") as client_cls:
            client_instance = MagicMock()
            client_cls.return_value.__enter__.return_value = client_instance
            client_instance.post.return_value.raise_for_status.return_value = None

            worker._on_message(channel, method, None, body, "http://platform-api:8000", Path("/storage"))

            client_instance.post.assert_called_once()
            channel.basic_ack.assert_called_once_with(delivery_tag="tag-1")

    def test_deve_disparar_callback_de_erro_quando_processamento_falhar(self) -> None:
        channel = Mock()
        method = SimpleNamespace(delivery_tag="tag-2")
        body = b"{}"

        with patch("worker._process_message", side_effect=ValueError("falha terminal")), patch(
            "worker._send_error_callback"
        ) as error_callback_mock:
            worker._on_message(channel, method, None, body, "http://platform-api:8000", Path("/storage"))

            error_callback_mock.assert_called_once()
            channel.basic_ack.assert_called_once_with(delivery_tag="tag-2")

    def test_deve_disparar_callback_de_erro_quando_post_de_resultado_falhar(self) -> None:
        channel = Mock()
        method = SimpleNamespace(delivery_tag="tag-3")
        body = b'{"analysis_id": "a-2", "object_key": "raw/a-2/original.png"}'

        with patch("worker._process_message", return_value=("a-2", "raw/a-2/original.png", "/tmp/page-1.png")), patch(
            "worker.analyze_architecture", return_value="{}"
        ), patch("worker.httpx.Client") as client_cls, patch("worker._send_error_callback") as error_callback_mock:
            client_instance = MagicMock()
            client_cls.return_value.__enter__.return_value = client_instance
            client_instance.post.return_value.raise_for_status.side_effect = RuntimeError("http failure")

            worker._on_message(channel, method, None, body, "http://platform-api:8000", Path("/storage"))

            error_callback_mock.assert_called_once()
            channel.basic_ack.assert_called_once_with(delivery_tag="tag-3")