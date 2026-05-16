from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid

from database import get_db
from models import Analysis, AnalysisStatus

app = FastAPI(title="Platform API")

@app.get("/")
def read_root():
    return {"message": "Welcome to Platform API"}

@app.get("/analyses", response_model=List[dict])
def list_analyses(db: Session = Depends(get_db)):
    analyses = db.query(Analysis).all()
    return [
        {
            "id": str(a.id),
            "status": a.status,
            "file_path": a.file_path,
            "checksum_sha256": a.checksum_sha256,
            "created_at": a.created_at,
            "updated_at": a.updated_at
        } for a in analyses
    ]

@app.get("/analyses/{analysis_id}")
def get_analysis(analysis_id: uuid.UUID, db: Session = Depends(get_db)):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {
        "id": str(analysis.id),
        "status": analysis.status,
        "file_path": analysis.file_path,
        "checksum_sha256": analysis.checksum_sha256,
        "created_at": analysis.created_at,
        "updated_at": analysis.updated_at
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
