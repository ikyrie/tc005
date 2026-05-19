# Hackathon - FIAP (IA4Devs)

* Matheus Alberto
* Ricarth Lima

## 1. Contexto

Este repositório contém o MVP final do Hackathon TC005 da FIAP.

A plataforma recebe diagramas de arquitetura, processa esse material com IA e entrega relatórios estruturados de risco com recomendações técnicas para mitigação.

A arquitetura final é 100% containerizada e orientada a microsserviços, com comunicação assíncrona entre API e Worker para garantir desacoplamento, robustez operacional e escalabilidade.

## 2. Pré-requisitos

* Docker instalado e em execução
* Docker Compose instalado
* Arquivo .env criado na raiz do projeto

Template sugerido para o arquivo .env:

```env
GEMINI_API_KEY=sua_chave_google_gemini
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
```

## 3. Como executar

Na raiz do projeto, execute:

```powershell
docker-compose up -d --build
```

Esse comando concentra toda a orquestração da solução.

Durante o processo, o Compose:

* Constrói as imagens dos serviços da aplicação
* Inicializa o PostgreSQL para persistência transacional
* Inicializa o RabbitMQ para mensageria assíncrona
* Publica a API FastAPI na porta 8000
* Inicializa o Worker de IA consumidor da fila
* Configura automaticamente os volumes compartilhados de storage entre API e Worker

Após a subida dos containers, a documentação interativa da API estará disponível em:

http://localhost:8000/docs

## 4. Visão da Arquitetura e IA

O fluxo de processamento foi projetado para suportar carga e falhas transitórias sem comprometer a continuidade do serviço.

Pontos-chave da arquitetura:

* Comunicação assíncrona robusta via RabbitMQ entre a API e o Worker
* Processamento desacoplado e tolerante a falhas, com confirmação de mensagens após tratamento
* Worker de IA baseado no modelo gemini-2.5-flash do Google
* Estratégia de resiliência com retries e backoff exponencial para instabilidades temporárias da nuvem, incluindo cenários de erro 503
* Compartilhamento de volumes para armazenamento de arquivos brutos, normalizados e relatórios processados

## 5. Validação do fluxo no Swagger

Com os containers ativos, valide o ciclo completo de análise pela interface Swagger.

* Acesse http://localhost:8000/docs
* Execute o endpoint POST /v1/analyses enviando um diagrama de arquitetura
* Copie o analysis_id retornado com status de processamento
* Consulte o resultado final no endpoint GET /v1/analyses/{analysis_id}/report
* Verifique o JSON processado contendo componentes, riscos e recomendações

## 6. Documentação complementar

Para aprofundamento técnico, consulte os materiais da pasta docs:

* [Visão do serviço de processamento por IA](docs/ai-processor.md)
* [Arquitetura da solução distribuída](docs/architecture.md)
* [Índice geral da documentação](docs/docs.md)
* [Guia de avaliação do projeto](docs/evaluation.md)
* [Detalhes técnicos da platform-api](docs/platform-api.md)
* [Esquemas e contratos de dados](docs/schemas.md)
* [Estratégia e estrutura de armazenamento](docs/storage.md)
