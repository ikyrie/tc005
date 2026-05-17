import uuid
import hashlib
import json
import time
import logging

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status, Request
from sqlalchemy import text
from sqlalchemy.orm import Session
from pathlib import Path

import pika

from database import get_db
from models import Analysis, AnalysisStatus

from messaging import publish_analysis_requested, RABBITMQ_URL
from schemas import ReportResponse, AnalysisStatusResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("platform_api")

STORAGE_RAW_DIR = Path("../storage/raw")
STORAGE_REPORTS_DIR = Path("../storage/reports")

STORAGE_RAW_DIR.mkdir(parents=True, exist_ok=True)
STORAGE_REPORTS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="SOAT Platform API")
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}


@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Captura ou gera um ID de rastreabilidade (Trace ID)
    trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4()))
    start_time = time.time()

    # Executa a requisição do usuário
    response = await call_next(request)

    # Calcula o tempo de processamento
    process_time_ms = (time.time() - start_time) * 1000

    # Cria o Log Estruturado em formato JSON estrito
    log_payload = {
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        "trace_id": trace_id,
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_ms": round(process_time_ms, 2)
    }

    logger.info(json.dumps(log_payload))

    # Devolve o Trace ID no cabeçalho da resposta para facilitar o debug do cliente
    response.headers["X-Trace-ID"] = trace_id
    return response


# --- ENDPOINT DE HEALTHCHECK ---
@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check(db: Session = Depends(get_db)):
    """Verifica a saúde da API, do Banco de Dados e do RabbitMQ."""
    health_status = {
        "status": "UP",
        "services": {
            "postgres": "DOWN",
            "rabbitmq": "DOWN"
        }
    }

    # 1. Testa Conexão com o Postgres
    try:
        db.execute(text("SELECT 1"))
        health_status["services"]["postgres"] = "UP"
    except Exception as e:
        logger.error(f"Healthcheck falhou no Postgres: {e}")
        health_status["status"] = "DOWN"

    # 2. Testa Conexão com o RabbitMQ
    try:
        parameters = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(parameters)
        if connection.is_open:
            health_status["services"]["rabbitmq"] = "UP"
            connection.close()
    except Exception as e:
        logger.error(f"Healthcheck falhou no RabbitMQ: {e}")
        health_status["status"] = "DOWN"

    # Se qualquer serviço essencial caiu, responde 503 Service Unavailable
    if health_status["status"] == "DOWN":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=health_status)

    return health_status


@app.post("/v1/analyses", status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, detail="Formato de arquivo não suportado")

    analysis_id = uuid.uuid4()
    analysis_dir = STORAGE_RAW_DIR / str(analysis_id)
    analysis_dir.mkdir(parents=True, exist_ok=True)

    file_path_disk = analysis_dir / f"original{ext}"
    file_path_db = f"raw/{analysis_id}/original{ext}"

    sha256_hash = hashlib.sha256()
    try:
        with open(file_path_disk, "wb") as buffer:
            while chunk := await file.read(8192):
                buffer.write(chunk)
                sha256_hash.update(chunk)
    except Exception:
        raise HTTPException(
            status_code=500, detail="Erro ao salvar arquivo no disco")

    new_analysis = Analysis(
        id=analysis_id,
        status=AnalysisStatus.RECEIVED,
        file_path=file_path_db,
        checksum_sha256=sha256_hash.hexdigest()
    )
    db.add(new_analysis)
    db.commit()
    db.refresh(new_analysis)

    try:
        publish_analysis_requested(
            analysis_id=new_analysis.id, file_path=new_analysis.file_path)
        new_analysis.status = AnalysisStatus.PROCESSING
        db.commit()
    except Exception as e:
        print(f"Aviso: Erro ao publicar na fila: {e}")

    return {"analysis_id": new_analysis.id, "status": new_analysis.status}


@app.get("/v1/analyses/{id}/status", response_model=AnalysisStatusResponse)
async def get_analysis_status(id: uuid.UUID, db: Session = Depends(get_db)):
    """Consulta o status atual da análise no banco de dados."""
    analysis = db.query(Analysis).filter(Analysis.id == id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Análise não encontrada")

    return {"analysis_id": analysis.id, "status": analysis.status}


@app.post("/v1/internal/analyses/{id}/callback", status_code=status.HTTP_200_OK)
async def analysis_callback(id: uuid.UUID, payload: ReportResponse, db: Session = Depends(get_db)):
    """
    Endpoint interno chamado pelo Worker de IA (Pessoa B).
    Garante a entrega dos 3 blocos, gera os arquivos físicos e atualiza o banco.
    """
    analysis = db.query(Analysis).filter(Analysis.id == id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Análise não encontrada")

    # Cria a pasta do relatório no storage compartilhado
    report_dir = STORAGE_REPORTS_DIR / str(id)
    report_dir.mkdir(parents=True, exist_ok=True)

    # 1. Salva o report.json bruto no disco
    json_path = report_dir / "report.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload.model_dump(), f, ensure_ascii=False, indent=4)

    # 2. Gera a versão em Markdown (report.md) exigida pelo edital
    md_path = report_dir / "report.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Relatório de Análise do Edital - {id}\n\n")
        f.write("## 1. Componentes Identificados\n")
        for comp in payload.componentes:
            f.write(f"- {comp}\n")
        f.write("\n## 2. Riscos Mapeados\n")
        for risco in payload.riscos:
            f.write(f"- {risco}\n")
        f.write("\n## 3. Recomendações de Mitigação\n")
        for rec in payload.recomendacoes:
            f.write(f"- {rec}\n")

    # 3. Atualiza o status no banco de dados para ANALYZED
    analysis.status = AnalysisStatus.ANALYZED
    db.commit()

    return {"message": "Callback processado e relatórios consolidados com sucesso"}


@app.get("/v1/analyses/{id}/report", response_model=ReportResponse)
async def get_analysis_report(id: uuid.UUID, db: Session = Depends(get_db)):
    """Retorna o relatório final se estiver pronto, caso contrário responde 404."""
    analysis = db.query(Analysis).filter(Analysis.id == id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Análise não encontrada")

    # Critério mínimo de aceitação: responder 404 enquanto não estiver pronto!
    if analysis.status != AnalysisStatus.ANALYZED:
        raise HTTPException(
            status_code=404,
            detail="O relatório ainda está sendo processado ou ocorreu um erro."
        )

    # Caminho do arquivo JSON no disco
    json_path = STORAGE_REPORTS_DIR / str(id) / "report.json"

    if not json_path.exists():
        raise HTTPException(
            status_code=500, detail="Arquivo de relatório sumiu do disco")

    # Lê do disco e devolve para o cliente o JSON estruturado
    with open(json_path, "r", encoding="utf-8") as f:
        report_data = json.load(f)

    return report_data
