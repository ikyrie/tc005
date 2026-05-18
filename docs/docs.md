# docs

Esta pasta centraliza a documentação funcional e técnica do projeto, reunindo especificações de API, visão arquitetural e descrições dos diretórios principais da solução. O objetivo é servir como ponto de navegação para entendimento do fluxo fim a fim, tanto do backend transacional quanto do worker de IA e dos contratos estruturados.

## architecture.md

Descreve o fluxo assíncrono entre o usuário, a Platform API, o armazenamento compartilhado, o RabbitMQ e o AI Processor usando um diagrama Mermaid. O arquivo é a visão macro de integração do sistema e ajuda a contextualizar como uploads, processamento de IA, callbacks internos e consulta de relatório se conectam.

## openapi.yaml

Formaliza a superfície HTTP pública da Platform API em OpenAPI 3.1. O documento especifica upload de arquivos, consulta de status e recuperação de relatórios, permitindo alinhar contratos entre implementação, documentação externa e futuros clientes integradores.

## ai-processor.md

Documenta a pasta do worker de IA, cobrindo o consumo de fila, a normalização de arquivos e a integração com o Gemini. Este arquivo conecta os artefatos operacionais do processamento assíncrono com o restante da arquitetura do sistema.

## platform-api.md

Documenta a API principal, a camada de persistência e a infraestrutura de migrations. Ele detalha como a aplicação recebe arquivos, persiste o estado das análises e prepara o backend para o fluxo assíncrono.

## evaluation.md

Documenta o script de avaliação local das análises multimodais. A página explica o uso de amostras locais e a exportação de métricas em CSV para inspeção rápida do comportamento do modelo.

## schemas.md

Documenta o contrato estruturado da saída do LLM e os enums usados para reduzir ambiguidade no domínio. Esta página é o elo entre o schema Pydantic e os consumidores do JSON retornado pela IA.

## storage.md

Documenta a função do volume local compartilhado no projeto, incluindo a área destinada aos arquivos brutos recebidos e aos artefatos gerados nos fluxos de processamento. É uma referência útil para operação local, containerização e depuração de pipelines.