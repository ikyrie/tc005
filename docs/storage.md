# storage

Esta pasta representa o volume compartilhado em disco usado pelos serviços para trocar artefatos sem depender de armazenamento externo. Ela funciona como fronteira física entre upload, normalização e persistência de arquivos temporários ou derivados dentro do MVP.

## raw/

Abriga os arquivos originais recebidos pela Platform API, organizados por analysis_id no padrão raw/{id}/original.ext. Esse diretório é lido posteriormente pelo worker de IA para localizar o documento fonte informado no object_key da mensagem publicada na fila.