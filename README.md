# Hackathon - FIAP (IA4Devs)

* Matheus Alberto
* Ricarth Lima

## 1. Contexto

Este repositório contém o MVP final do Hackathon TC005 da FIAP.

A plataforma recebe diagramas de arquitetura, processa esse material com IA e entrega relatórios estruturados de risco com recomendações técnicas para mitigação.

A arquitetura final é 100% containerizada e orientada a microsserviços, com comunicação assíncrona entre API e Worker para garantir desacoplamento, robustez operacional e escalabilidade.

Componentes principais da solução:

* Frontend Web (HTML, Vanilla JS e Tailwind CSS via CDN), servido por Nginx e totalmente desacoplado da API
* Platform API em FastAPI para upload, persistência e orquestração do fluxo de análise
* Worker de IA para processamento assíncrono e geração de relatório estruturado
* RabbitMQ para mensageria entre serviços
* PostgreSQL para persistência transacional
* Volumes de storage compartilhado para artefatos raw, normalizados e reports

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
* Publica o Frontend Web na porta 3000
* Publica a API FastAPI na porta 8000
* Inicializa o Worker de IA consumidor da fila
* Configura automaticamente os volumes compartilhados de storage entre API e Worker

Após a subida dos containers, acesse a aplicação principal no navegador em:

http://localhost:3000

Para testes diretos da API, a documentação interativa Swagger continua disponível em:

http://localhost:8000/docs

## 4. Visão da Arquitetura e IA

O fluxo de processamento foi projetado para suportar carga e falhas transitórias sem comprometer a continuidade do serviço.

Pontos-chave da arquitetura:

* Frontend desacoplado consumindo a API por HTTP, sem dependência direta de código entre camadas
* Comunicação assíncrona robusta via RabbitMQ entre a API e o Worker
* Processamento desacoplado e tolerante a falhas, com confirmação de mensagens após tratamento
* Worker de IA baseado no modelo gemini-2.5-flash do Google
* Estratégia de resiliência com retries e backoff exponencial para instabilidades temporárias da nuvem, incluindo cenários de erro 503
* Compartilhamento de volumes para armazenamento de arquivos brutos, normalizados e relatórios processados

## 5. Fluxo de uso pela interface visual

Com os containers ativos, a experiência recomendada é validar o ciclo completo pela interface web.

* Acesse a página inicial em http://localhost:3000
* Faça o upload do diagrama de arquitetura
* Aguarde a tela animada de processamento da IA
* Visualize o resultado final com a funcionalidade Antes e Depois, exibindo a imagem original lado a lado com componentes, riscos e recomendações

## 6. Testes alternativos via Swagger

Para validações de contrato, integrações via código ou testes técnicos de endpoint, utilize o Swagger.

* Acesse http://localhost:8000/docs
* Execute o endpoint POST /v1/analyses enviando um diagrama de arquitetura
* Copie o analysis_id retornado com status de processamento
* Consulte o resultado final no endpoint GET /v1/analyses/{analysis_id}/report
* Verifique o JSON processado contendo componentes, riscos e recomendações

## 7. Testes Automatizados

O projeto utiliza o framework Pytest para garantir a confiabilidade dos microsserviços `platform-api` e `ai-processor`. Os testes automatizados cobrem cenários críticos de integração e validação de funcionalidades, assegurando que os serviços operem conforme esperado. Além disso, há uma preocupação contínua com a cobertura de código (coverage), que é monitorada para identificar áreas que necessitam de maior atenção.

## 8. Documentação complementar

Para aprofundamento técnico, consulte os materiais da pasta docs:

* [Visão do serviço de processamento por IA](docs/ai-processor.md)
* [Arquitetura da solução distribuída](docs/architecture.md)
* [Índice geral da documentação](docs/docs.md)
* [Guia de avaliação do projeto](docs/evaluation.md)
* [Detalhes técnicos da platform-api](docs/platform-api.md)
* [Esquemas e contratos de dados](docs/schemas.md)
* [Estratégia e estrutura de armazenamento](docs/storage.md)
