from typing import List
from uuid import UUID

from pydantic import BaseModel, Field


class ReportResponse(BaseModel):
    componentes: List[str] = Field(...,
                                   description="Lista de componentes identificados no edital")
    riscos: List[str] = Field(...,
                              description="Lista de riscos jurídicos/técnicos mapeados")
    recomendacoes: List[str] = Field(...,
                                     description="Lista de recomendações de mitigação")


class AnalysisStatusResponse(BaseModel):
    analysis_id: UUID
    status: str
