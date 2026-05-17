# platform-api

Esta pasta reúne a API principal do sistema, responsável por receber uploads, persistir metadados das análises e expor a superfície HTTP consumida pelos clientes e pelo processador de IA. O diretório combina FastAPI, SQLAlchemy e Alembic para oferecer uma camada síncrona de entrada e consulta sobre um fluxo de processamento assíncrono.

## src/main.py

Define a aplicação FastAPI e o endpoint de criação de análises. O arquivo valida extensões permitidas, gera o UUID da análise, grava o arquivo bruto em storage/raw, calcula o checksum SHA-256 em streaming e persiste o registro no banco via SQLAlchemy. Ele conecta a API com o armazenamento em disco e com a camada de modelos, preparando a base para que o worker consuma o arquivo depois.

## src/models.py

Declara os modelos ORM da aplicação com SQLAlchemy 2, incluindo o enum AnalysisStatus e a entidade Analysis. O arquivo estabelece o contrato de persistência dos dados principais da análise, como status, caminho do arquivo, checksum e timestamps, servindo tanto para a API quanto para as migrações do Alembic.

## src/database.py

Centraliza a criação do engine SQLAlchemy, da SessionLocal e da dependência get_db usada pelo FastAPI. O módulo conecta a aplicação ao PostgreSQL local e define a mecânica de abertura e fechamento de sessões transacionais por requisição.

## requirements.txt

Agrupa as dependências da Platform API, como FastAPI, Uvicorn, SQLAlchemy, Alembic, psycopg2-binary, python-multipart e Pydantic. Ele representa o conjunto mínimo necessário para subir a API, manipular uploads e manter a integração com o banco de dados.

## Dockerfile

Descreve a imagem de execução da Platform API a partir de python:3.14-slim. O build copia requirements.txt, instala dependências, replica o código para /app, configura PYTHONPATH para /app/src e inicia o Uvicorn na porta 8000. Este arquivo conecta a API ao ambiente containerizado esperado pelo docker-compose e pelos fluxos locais.

## bootstrap.ps1

Automatiza a preparação do ambiente de desenvolvimento no Windows com PowerShell. O script sobe o PostgreSQL via Docker Compose, cria a virtualenv, instala dependências, garante a pasta de migrations, executa o Alembic e inicia a aplicação com Uvicorn. É o ponto operacional mais direto para colocar a Platform API em funcionamento sem executar os passos manualmente.

## alembic.ini

Contém a configuração do Alembic, incluindo a localização das migrations, a URL padrão do banco e a configuração de logging do processo de migração. O arquivo serve como base de execução para revision, upgrade e demais comandos do ciclo de vida do schema.

## alembic/env.py

Configura o contexto de execução do Alembic e injeta o metadata dos modelos da aplicação ao ajustar o sys.path para o diretório src. O script é responsável por ligar a infraestrutura de migrations ao modelo ORM real, tanto em modo offline quanto online.

## alembic/versions/8b72b4bc55a9_create_analyses_table.py

Implementa a migration inicial do projeto, criando a tabela analyses com UUID, enum de status, caminho do arquivo, checksum e timestamps. Este arquivo materializa no banco o contrato definido em src/models.py e inaugura o histórico de versionamento do schema.

## alembic/script.py.mako

É o template padrão usado pelo Alembic para gerar novos arquivos de migration. Embora não contenha regra de negócio, participa da padronização do versionamento do schema e da automação do fluxo de evolução do banco.

## alembic/README

Arquivo auxiliar gerado pelo Alembic para explicar a estrutura básica da pasta de migrations. Ele tem função mais operacional do que de domínio, servindo como referência rápida para manutenção do ambiente.

## README.md

Documenta pré-requisitos, instalação, execução local e testes da Platform API. O conteúdo ajuda a conectar a pasta com o fluxo de desenvolvimento, indicando o uso do PYTHONPATH, da documentação Swagger e da configuração de banco padrão usada pelos módulos Python.