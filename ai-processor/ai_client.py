from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image
from google import genai
from google.genai import types

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from schemas.analysis_result import AnalysisResult


SYSTEM_INSTRUCTION = (
    "Você é um arquiteto de software sênior. Analise este diagrama de arquitetura, "
    "identifique os componentes, aponte os riscos de segurança ou escalabilidade e "
    "forneça recomendações de mitigação."
)

client = genai.Client()


def analyze_architecture(image_path: str) -> str:
    with Image.open(image_path) as image:
        response = client.models.generate_content(
            model="gemini-3.1-pro",
            contents=[image],
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_schema=AnalysisResult,
                response_mime_type="application/json",
            ),
        )

    return response.text