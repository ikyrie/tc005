# ai-processor

Esta pasta concentra o worker assíncrono responsável por consumir solicitações de análise, normalizar os arquivos de entrada, executar a análise multimodal com o Gemini e devolver o resultado estruturado para a Platform API. O diretório funciona como o núcleo do pipeline de IA e depende de armazenamento compartilhado em disco, RabbitMQ e chamadas HTTP internas para fechar o fluxo.

## worker.py

Implementa o consumidor da fila analysis.requested.v1 com a biblioteca pika e usa logging estruturado para rastrear cada etapa do processamento. O arquivo lê as variáveis de ambiente de infraestrutura, resolve o caminho físico do arquivo bruto em storage, chama normalizer.normalize_to_png para gerar uma imagem padronizada, invoca ai_client.analyze_architecture para obter o JSON estruturado da IA e publica o resultado na Platform API via httpx. O tratamento de erro captura falhas de normalização, integração e callback, envia o endpoint interno de erro e sempre faz basic_ack da mensagem para evitar reprocessamento infinito no broker.

## ai_client.py

Encapsula a chamada ao SDK oficial google-genai para análise do diagrama já normalizado. O módulo ajusta o sys.path para alcançar a raiz do projeto, importa o schema Pydantic schemas.analysis_result.AnalysisResult como contrato de saída e abre a imagem com Pillow antes de chamar client.models.generate_content no modelo gemini-3.1-pro. A configuração usa GenerateContentConfig com response_schema e response_mime_type application/json para forçar resposta estruturada, enquanto tenacity adiciona retentativas com backoff exponencial para falhas transitórias de conexão e timeout.

## normalizer.py

Fornece a função procedural normalize_to_png, que recebe o arquivo original e produz uma imagem PNG padronizada em storage/normalized/{analysis_id}/page-1.png. O código usa PyMuPDF para renderizar estritamente a primeira página de PDFs e Pillow para converter imagens JPG, JPEG e PNG para RGB antes de salvar. O módulo centraliza a validação de formatos suportados e converte erros de arquivo corrompido, formato inválido ou leitura falha em exceções consistentes para o worker tratar.

## requirements.txt

Lista as dependências de runtime do worker de IA, incluindo pika para RabbitMQ, httpx para callbacks HTTP, Pillow e PyMuPDF para normalização de arquivos, google-genai para integração com o Gemini e tenacity para retentativas. Este arquivo é o ponto de instalação mínimo para executar o pipeline fora de contêiner ou em futuras imagens Docker.

## Dockerfile

Existe como placeholder de containerização do serviço de IA, mas no estado atual está vazio. A presença do arquivo indica a intenção de empacotar o worker como serviço independente, porém ainda sem definição efetiva de build, instalação de dependências ou comando de inicialização.