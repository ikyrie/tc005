from __future__ import annotations

import json
import logging
import os
from pathlib import Path

import httpx
import pika
from dotenv import load_dotenv

from ai_client import analyze_architecture
from normalizer import normalize_to_png


QUEUE_NAME = "analysis.requested.v1"


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)


def _get_settings() -> tuple[str, Path, str]:
    rabbitmq_url = os.getenv(
        "RABBITMQ_URL",
        "amqp://guest:guest@rabbitmq:5672/%2F",
    )
    default_storage_base_dir = Path(__file__).resolve().parents[1] / "storage"
    storage_base_dir = Path(os.getenv("STORAGE_BASE_DIR", str(default_storage_base_dir))).resolve()
    platform_api_url = os.getenv("PLATFORM_API_URL", "http://localhost:8000")
    return rabbitmq_url, storage_base_dir, platform_api_url


def _send_error_callback(platform_api_url: str, analysis_id: str, error_message: str) -> None:
    callback_url = f"{platform_api_url}/internal/v1/analyses/{analysis_id}/error"
    payload = {
        "error_code": "NORMALIZATION_FAILED",
        "error_message": error_message,
    }

    with httpx.Client(timeout=10.0) as client:
        response = client.post(callback_url, json=payload)
        response.raise_for_status()


def _process_message(body: bytes, storage_base_dir: Path) -> tuple[str, str, str]:
    payload = json.loads(body.decode("utf-8"))

    analysis_id = str(payload["analysis_id"])
    object_key = str(payload["file_path"])
    input_path = (storage_base_dir / object_key.lstrip("/\\")).resolve()
    output_base_dir = storage_base_dir / "normalized"

    normalized_path = normalize_to_png(
        input_path=str(input_path),
        output_base_dir=str(output_base_dir),
        analysis_id=analysis_id,
    )
    return analysis_id, object_key, normalized_path


def _on_message(
    channel: pika.adapters.blocking_connection.BlockingChannel,
    method: pika.spec.Basic.Deliver,
    properties: pika.spec.BasicProperties,  # noqa: ARG001  # pylint: disable=unused-argument
    body: bytes,
    platform_api_url: str,
    storage_base_dir: Path,
) -> None:
    analysis_id = "unknown"

    try:
        analysis_id, object_key, normalized_path = _process_message(body, storage_base_dir)
        logger.info(
            "normalization_succeeded analysis_id=%s object_key=%s output_path=%s",
            analysis_id,
            object_key,
            normalized_path,
        )
        result_json = analyze_architecture(normalized_path)
        callback_url = f"{platform_api_url}/v1/internal/analyses/{analysis_id}/callback"
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                callback_url,
                content=result_json,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()

        logger.info("result_callback_sent analysis_id=%s", analysis_id)
    except Exception as exc:
        error_message = str(exc)
        logger.exception(
            "normalization_failed analysis_id=%s error=%s",
            analysis_id,
            error_message,
        )

        try:
            _send_error_callback(platform_api_url, analysis_id, error_message)
            logger.info(
                "error_callback_sent analysis_id=%s error_code=NORMALIZATION_FAILED",
                analysis_id,
            )
        except Exception:
            logger.exception(
                "error_callback_failed analysis_id=%s",
                analysis_id,
            )
    finally:
        try:
            channel.basic_ack(delivery_tag=method.delivery_tag)
            logger.info("message_acknowledged analysis_id=%s", analysis_id)
        except Exception:
            logger.exception("ack_failed analysis_id=%s", analysis_id)


def main() -> None:
    rabbitmq_url, storage_base_dir, platform_api_url = _get_settings()

    logger.info(
        "worker_starting queue=%s storage_base_dir=%s platform_api_url=%s",
        QUEUE_NAME,
        storage_base_dir,
        platform_api_url,
    )

    connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(
        queue=QUEUE_NAME,
        on_message_callback=lambda ch, method, properties, body: _on_message(
            ch,
            method,
            properties,
            body,
            platform_api_url,
            storage_base_dir,
        ),
    )

    logger.info("worker_listening queue=%s", QUEUE_NAME)
    channel.start_consuming()


if __name__ == "__main__":
    load_dotenv()
    main()
