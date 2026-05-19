FROM python:3.11-slim

WORKDIR /app

COPY services/ai-processor/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY schemas/ /app/schemas/
COPY services/ai-processor/ /app/services/ai-processor/

WORKDIR /app/services/ai-processor

CMD ["python", "worker.py"]
