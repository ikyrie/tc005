# evaluation

Esta pasta agrupa o fluxo de avaliação manual do processador de IA a partir de imagens locais. O objetivo é permitir testes exploratórios do modelo, coletando métricas simples por arquivo sem depender do broker, da Platform API ou do pipeline completo de produção.

## evaluate.py

Implementa um script procedural que ajusta o sys.path para a raiz do projeto, importa a função de análise do módulo de IA e percorre as imagens em evaluation/samples. Para cada arquivo PNG ou JPG, o script chama analyze_architecture, faz o parse do JSON retornado e extrai a quantidade de componentes e riscos identificados. O resultado é salvo em evaluation/evaluation.csv com a indicação de sucesso por amostra; em caso de falha, o script registra contagens zeradas para manter a saída consolidada.