# Hackathon para IA4Devs API e Microsserviços

* Matheus Alberto
* Ricarth Lima

## 1. Contexto do hackathon

Este repositório contém o projeto final do hackathon **TC005 da FIAP**.

A solução foi desenvolvida como um **sistema distribuído baseado em microsserviços**, com comunicação assíncrona entre componentes.

O objetivo da plataforma é permitir o upload de diagramas de arquitetura para que um serviço de Inteligência Artificial processe o material e gere **relatórios automatizados de risco**, incluindo **recomendações de melhoria** para a arquitetura analisada.

## 2. Como rodar a aplicação

Siga os passos abaixo na ordem para instalar as dependências e subir todo o fluxo:

### 1. Na raiz do projeto, suba a infraestrutura base (banco de dados e mensageria):

```powershell
docker-compose up -d
```

### 2. Ative o seu ambiente virtual e instale as dependências de cada serviço:

```powershell
.\.venv\Scripts\activate
pip install -r services/platform-api/requirements.txt
pip install -r services/ai-processor/requirements.txt

```

### 3. Inicie a API executando o bootstrap do serviço `platform-api`:

```powershell
cd services/platform-api
.\bootstrap.ps1
```

A API será exposta com Swagger em
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 4. Em um terminal separado, com o ambiente virtual ativado, execute o worker de IA a partir da raiz do repositório:

```powershell
.\.venv\Scripts\activate
python services/ai-processor/worker.py
```

## 3. Como testar o fluxo completo

Após garantir que a infraestrutura, a API e o worker estão rodando, siga este passo a passo para testar a plataforma:

1. Acesse o Swagger no seu navegador: `http://127.0.0.1:8000/docs`
2. Encontre o endpoint de upload (`POST /v1/analyses`).
3. Faça o upload de um arquivo de imagem contendo um diagrama de arquitetura (exemplo: uma arquitetura AWS).
4. O Swagger retornará o status `PROCESSING` e um campo `analysis_id`. Copie esse ID.
5. Observe o terminal onde o worker de IA está rodando. Você verá os logs de recebimento da imagem e o processamento da análise via IA.
6. Volte ao Swagger e utilize o endpoint de consulta (`GET /v1/analyses/{analysis_id}`), colando o ID copiado.
7. O sistema retornará o JSON completo com o status `COMPLETED` e o relatório detalhado gerado pela Inteligência Artificial.

## 4. Como rodar os testes

O projeto possui testes unitários para validar o isolamento entre componentes e garantir o comportamento esperado dos serviços.

### 1. Ative o ambiente virtual (caso não esteja ativado):

```powershell
.\.venv\Scripts\Activate.ps1
cd ../..
```

### 2. Execute a suíte de testes com cobertura:

```powershell
pytest services/ --cov=services/ai-processor --cov=services/platform-api --cov-report=term-missing
```

## 5. Documentação adicional

Detalhes arquiteturais aprofundados, decisões técnicas e especificações complementares estão documentados nos arquivos da pasta `docs/`.

Consulte esse diretório para obter entendimento completo da solução, dos contratos e dos direcionamentos técnicos do projeto.

Arquivos disponíveis em `docs/`:

* [Visão do serviço de processamento por IA](https://www.google.com/search?q=docs/ai-processor.md)
* [Arquitetura da solução distribuída](https://www.google.com/search?q=docs/architecture.md)
* [Índice geral da documentação](https://www.google.com/search?q=docs/docs.md)
* [Guia de avaliação do projeto](https://www.google.com/search?q=docs/evaluation.md)
* [Detalhes técnicos da platform-api](https://www.google.com/search?q=docs/platform-api.md)
* [Esquemas e contratos de dados](https://www.google.com/search?q=docs/schemas.md)
* [Estratégia e estrutura de armazenamento](https://www.google.com/search?q=docs/storage.md)
