# schemas

Esta pasta concentra o contrato tipado da saída produzida pelo modelo de IA. O objetivo do diretório é garantir que o resultado da análise arquitetural seja previsível, validável e reutilizável por outros componentes do sistema, reduzindo ambiguidade entre geração multimodal, persistência e consumo posterior.

## analysis_result.py

Define o schema Pydantic AnalysisResult e os submodelos que representam componentes, riscos, recomendações e metadados do modelo. O arquivo usa BaseModel, Enum e Field do Pydantic para estruturar a resposta do LLM, combinando extra=forbid e enums explícitos para evitar campos livres e classificações inconsistentes. Ele é consumido diretamente por ai-processor/ai_client.py como response_schema do Gemini e serve como contrato central entre a geração da IA e o restante do backend.
