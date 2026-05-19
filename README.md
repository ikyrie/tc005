# Hackathon para IA4Devs - FIAP
 
- Matheus Alberto
- Ricarth Lima

## 1. Contexto do hackathon

Este repositório contém o projeto final do hackathon **TC005 da FIAP**.

A solução foi desenvolvida como um **sistema distribuído baseado em microsserviços**, com comunicação assíncrona entre componentes.

O objetivo da plataforma é permitir o upload de diagramas de arquitetura para que um serviço de Inteligência Artificial processe o material e gere **relatórios automatizados de risco**, incluindo **recomendações de melhoria** para a arquitetura analisada.

## 2. Como rodar a aplicação

Siga os passos abaixo na ordem para subir todo o fluxo:

1. Na raiz do projeto, suba a infraestrutura base (banco de dados e mensageria):

```powershell
docker-compose up -d
```

2. Inicie a API executando o bootstrap do serviço `platform-api`:

```powershell
cd services/platform-api
.\bootstrap.ps1
```

A API será exposta com Swagger em:

```text
http://127.0.0.1:8000/docs
```

3. Em um terminal separado, com o ambiente virtual ativado, execute o worker de IA a partir da raiz do repositório:

```powershell
cd services/platform-api
.\.venv\Scripts\Activate.ps1
cd ../..
python services/ai-processor/worker.py
```

## 3. Como rodar os testes

O projeto possui testes unitários para validar o isolamento entre componentes e garantir o comportamento esperado dos serviços.

1. Ative o ambiente virtual:

```powershell
cd services/platform-api
.\.venv\Scripts\Activate.ps1
cd ../..
```

2. Execute a suíte de testes com cobertura:

```powershell
pytest services/ --cov=services/ai-processor --cov=services/platform-api --cov-report=term-missing
```

## 4. Documentação adicional

Detalhes arquiteturais aprofundados, decisões técnicas e especificações complementares estão documentados nos arquivos da pasta `docs/`.

Consulte esse diretório para obter entendimento completo da solução, dos contratos e dos direcionamentos técnicos do projeto.

Arquivos disponíveis em `docs/`:

- [Visão do serviço de processamento por IA](docs/ai-processor.md)
- [Arquitetura da solução distribuída](docs/architecture.md)
- [Índice geral da documentação](docs/docs.md)
- [Guia de avaliação do projeto](docs/evaluation.md)
- [Detalhes técnicos da platform-api](docs/platform-api.md)
- [Esquemas e contratos de dados](docs/schemas.md)
- [Estratégia e estrutura de armazenamento](docs/storage.md)

## 5. Criadores / estudantes


