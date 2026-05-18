import os
import uuid
import hashlib
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pathlib import Path

from database import get_db, engine
from models import Analysis, Base, AnalysisStatus

# Garante que os diretórios de armazenamento existam
STORAGE_RAW_DIR = Path("../storage/raw")
STORAGE_RAW_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="SOAT Platform API")

# Lista de extensões permitidas pelo edital
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}


@app.post("/v1/analyses", status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # 1. Validação de extensão
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, detail="Formato de arquivo não suportado")

    # 2. Gera UUID da análise e prepara caminhos
    analysis_id = uuid.uuid4()
    analysis_dir = STORAGE_RAW_DIR / str(analysis_id)
    analysis_dir.mkdir(parents=True, exist_ok=True)

    file_path_disk = analysis_dir / f"original{ext}"
    # Caminho relativo para o banco
    file_path_db = f"raw/{analysis_id}/original{ext}"

    # 3. Salva no disco e calcula o SHA-256 de forma otimizada (em chunks)
    sha256_hash = hashlib.sha256()

    try:
        with open(file_path_disk, "wb") as buffer:
            while chunk := await file.read(8192):  # Lê de 8 em 8 KB
                buffer.write(chunk)
                sha256_hash.update(chunk)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Erro ao salvar arquivo no disco")

    # 4. Salva o registro no banco de dados
    new_analysis = Analysis(
        id=analysis_id,
        status=AnalysisStatus.RECEIVED,
        file_path=file_path_db,
        checksum_sha256=sha256_hash.hexdigest()
    )

    db.add(new_analysis)
    db.commit()
    db.refresh(new_analysis)

    # 5. Retorna o contrato estipulado
    return {
        "analysis_id": new_analysis.id,
        "status": new_analysis.status
    }
