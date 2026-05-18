FROM python:3.12-slim

WORKDIR /app

COPY services/ai-processor/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY services/ai-processor/ /app/services/ai-processor/
COPY schemas/ /app/schemas/

CMD ["python", "/app/services/ai-processor/worker.py"]
