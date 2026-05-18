---
applyTo: "services/platform-api/**/*"
---
# Escopo: Platform API (Pessoa A)
Esta pasta contém a API principal do sistema (BFF/Gateway).

* Stack: FastAPI, SQLAlchemy 2, Alembic, PostgreSQL 16.
* Responsabilidades: Upload de arquivos, consulta de status, roteamento de callbacks internos e persistência de estado.
* Regra de Upload: O endpoint `/v1/analyses` deve salvar o arquivo em disco, registrar no banco com status `RECEIVED` e publicar um evento na fila `analysis.requested.v1`.
* Validação: Falhas no formato devem retornar HTTP 415. Tamanho excedido deve retornar HTTP 413.