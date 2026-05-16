# Arquitetura do Sistema e Fluxo de Dados

O diagrama abaixo representa a interação assíncrona entre a Plataforma (Pessoa A) e o Processador de IA (Pessoa B) utilizando armazenamento local compartilhado e RabbitMQ.

```mermaid
sequenceDiagram
    autonumber
    Actor Usuario as Usuário/Cliente
    Participant API as Platform API (Pessoa A)
    Participant Disk as Storage (Volume Compartilhado)
    Participant Queue as RabbitMQ (Broker)
    Participant Worker as AI Processor (Pessoa B)

    Usuario->>API: POST /v1/analyses (Envia arquivo)
    Note over API: Calcula SHA-256 e<br/>gera UUID da análise
    API->>Disk: Salva arquivo em /storage/raw/{id}/original.pdf
    API->>Queue: Publica evento (analysis.requested.v1) com o caminho do arquivo
    API-->>Usuario: Retorna 201 Created (analysis_id, status: RECEIVED)

    Queue->>Worker: Consome mensagem da fila
    Worker->>Disk: Lê o arquivo direto de /storage/raw/...
    Note over Worker: Processa IA (Componentes, Riscos, Recomendações)
    Worker->>Disk: Salva resultado em /storage/reports/{id}/report.json
    Worker->>API: Dispara Callback Interno (Status: ANALYZED / ERROR)
    Note over API: Atualiza Status no Banco de Dados

    Usuario->>API: GET /v1/analyses/{id}/report
    alt Status ainda não é ANALYZED
        API-->>Usuario: Retorna 404 Not Found
    else Status é ANALYZED
        API->>Disk: Busca report.json em /storage/reports/...
        API-->>Usuario: Retorna 200 OK com o JSON de 3 blocos
    end
```
