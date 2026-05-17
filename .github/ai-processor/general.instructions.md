---
applyTo: "ai-processor/**/*"
---
# Escopo: AI Processor (Pessoa B)
Esta pasta contém o Worker de Inteligência Artificial que consome a fila e processa os diagramas.

* Stack: Python 3.12, Pydantic v2, PyMuPDF, cliente RabbitMQ/Redis.
* Responsabilidades: Normalizar PDFs/Imagens, integrar com LLM via prompt estruturado e garantir os guardrails da saída.
* Regra de Ouro (Zero Condicionais): Não escreva regras de negócio complexas (if/else) para classificar riscos. Use Pydantic e Enums para forçar a IA a responder no formato correto.
* Comunicação: O serviço não expõe endpoints REST externos. Ele escuta a fila, lê o arquivo do volume compartilhado (`raw/{id}/original.*`) e devolve o resultado fazendo um POST para o callback interno da Platform API.
* Resiliência: Em caso de timeout da IA ou saída fora do schema, aplique retentativas via código antes de marcar o status como erro.