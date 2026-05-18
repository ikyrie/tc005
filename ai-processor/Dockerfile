FROM python:3.12-slim

WORKDIR /app

COPY ai-processor/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ai-processor/ /app/ai-processor/
COPY schemas/ /app/schemas/

CMD ["python", "/app/ai-processor/worker.py"]
