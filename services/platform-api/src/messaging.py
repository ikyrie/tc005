import pika
import json
import logging

# Configuração de conexão com o RabbitMQ local via Docker
RABBITMQ_URL = "amqp://soat_user:soat_password@localhost:5672/"
QUEUE_NAME = "analysis.requested.v1"

logger = logging.getLogger(__name__)


def get_rabbitmq_channel():
    """Cria conexão e canal com o RabbitMQ, garantindo que a fila exista."""
    try:
        parameters = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        # Cria a fila se ela não existir.
        # durable=True garante que a fila sobreviva a reinícios do RabbitMQ.
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        return connection, channel
    except Exception as e:
        logger.error(f"Erro ao conectar no RabbitMQ: {e}")
        raise


def publish_analysis_requested(analysis_id: str, file_path: str):
    """
    Publica a mensagem de análise solicitada na fila.
    A mensagem contém apenas o ID e o caminho do arquivo, não o arquivo em si.
    """
    try:
        connection, channel = get_rabbitmq_channel()

        # O payload exigido para a Pessoa B saber o que fazer
        payload = {
            "analysis_id": str(analysis_id),
            "file_path": file_path
        }

        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=json.dumps(payload),
            properties=pika.BasicProperties(
                # Garante que a mensagem será salva em disco
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,
                content_type='application/json',
            )
        )

        logger.info(f"Mensagem publicada na fila {
                    QUEUE_NAME} para análise {analysis_id}")
        connection.close()
    except Exception as e:
        logger.error(f"Falha ao publicar mensagem no RabbitMQ: {e}")
        # Em um cenário ideal, você trataria o retry ou salvaria em uma tabela de outbox aqui
        raise
