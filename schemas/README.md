# Schemas de Analysis Result

Este diretório contém o contrato de dados para a saida estruturada do LLM que analisa diagramas de arquitetura de software.

Arquivo principal:
- `analysis_result.py`

## Objetivo do schema

O schema define, de forma estrita e tipada, como o resultado da analise deve ser retornado pelo modelo de IA.

Beneficios:
- Evita respostas livres e ambiguas do LLM.
- Facilita validacao automatica no backend.
- Reduz condicionais no codigo de aplicacao com uso de Enums.
- Padroniza o formato para persistencia, auditoria e geracao de relatorios.

## Visao geral da estrutura

A classe raiz e `AnalysisResult`. Ela representa um unico resultado de analise e contem:

- `analysis_id` (`UUID`): identificador unico da analise.
- `components` (`list[Component]`): componentes detectados no diagrama.
- `risks` (`list[Risk]`): riscos identificados.
- `recommendations` (`list[Recommendation]`): acoes recomendadas para mitigacao.
- `limitations` (`list[str]`): o que o modelo nao conseguiu observar ou inferir.
- `model` (`ModelMetadata`): metadados do provedor e nome do modelo usado.

## Enums e por que eles existem

### `ComponentKind`
Categorias normalizadas para componentes arquiteturais:
- `gateway`
- `database`
- `microservice`
- `queue`
- `cache`
- `frontend`
- `unknown`

Por que importa:
- Evita strings arbitrarias como `db`, `DB`, `database-server`.
- Simplifica regras de negocio que dependem do tipo de componente.

### `RiskSeverity`
Niveis de severidade para riscos:
- `LOW`
- `MEDIUM`
- `HIGH`
- `CRITICAL`

Por que importa:
- Permite ordenacao e priorizacao consistentes.
- Facilita politicas de alerta e SLA.

### `RecommendationPriority`
Prioridade de implementacao para recomendacoes:
- `LOW`
- `MEDIUM`
- `HIGH`

Por que importa:
- Organiza backlog tecnico com criterio uniforme.

## Submodelos

### `Component`
Representa um componente encontrado no diagrama.

Campos:
- `name` (`str`): nome legivel do componente.
- `kind` (`ComponentKind`): categoria normalizada.
- `description` (`str`): papel ou contexto do componente.

### `Risk`
Representa um risco arquitetural ou de seguranca.

Campos:
- `code` (`str`): identificador estavel em snake_case.
- `title` (`str`): titulo curto para exibicao.
- `severity` (`RiskSeverity`): nivel de severidade.
- `description` (`str`): explicacao detalhada do risco e impacto.

### `Recommendation`
Representa uma acao para mitigar riscos.

Campos:
- `title` (`str`): titulo curto da recomendacao.
- `priority` (`RecommendationPriority`): urgencia de implementacao.
- `description` (`str`): orientacao pratica do que fazer e por que.

### `ModelMetadata`
Representa dados do modelo que gerou a analise.

Campos:
- `provider` (`str`): provedor do modelo.
- `model_name` (`str`): identificador exato do modelo.

## Regras de validacao importantes

Todos os modelos usam Pydantic V2 com configuracao para maior seguranca:

- `extra="forbid"`: rejeita campos nao previstos no contrato.
- `str_strip_whitespace=True` (nos submodelos textuais): remove espacos extras nas bordas de strings.

Impacto pratico:
- Se o LLM retornar campos inesperados, o payload falha na validacao.
- Se houver ruido textual com espacos no inicio/fim, a normalizacao e automatica.

## Papel de `Field(description=...)` em Structured Outputs

Cada atributo possui `Field(description="...")` para:
- Guiar o LLM sobre semantica e expectativa de cada campo.
- Reduzir interpretacoes erradas na geracao de JSON.
- Melhorar a qualidade de extrações em cenarios de visao + texto.

Em fluxos de Structured Outputs, essas descricoes funcionam como instrucoes contextuais diretamente acopladas ao schema.

## Exemplo de payload valido

```json
{
  "analysis_id": "8f4cfe5f-48d8-40da-95c4-2ec0af393f1d",
  "components": [
    {
      "name": "API Gateway",
      "kind": "gateway",
      "description": "Entry point for external client traffic."
    },
    {
      "name": "Orders Service",
      "kind": "microservice",
      "description": "Handles order lifecycle and business rules."
    }
  ],
  "risks": [
    {
      "code": "missing_authentication_between_services",
      "title": "Service-to-service calls without authentication",
      "severity": "HIGH",
      "description": "Internal requests appear to be unauthenticated, enabling lateral movement."
    }
  ],
  "recommendations": [
    {
      "title": "Enforce mTLS for internal communication",
      "priority": "HIGH",
      "description": "Implement mTLS between services and rotate certificates regularly."
    }
  ],
  "limitations": [
    "Network segmentation boundaries are not visible in the diagram."
  ],
  "model": {
    "provider": "OpenAI",
    "model_name": "gpt-4.1"
  }
}
```

## Como usar no codigo

Exemplo minimo de validacao:

```python
from schemas.analysis_result import AnalysisResult

payload = {
    "analysis_id": "8f4cfe5f-48d8-40da-95c4-2ec0af393f1d",
    "components": [],
    "risks": [],
    "recommendations": [],
    "limitations": [],
    "model": {"provider": "OpenAI", "model_name": "gpt-4.1"},
}

result = AnalysisResult.model_validate(payload)
```

Se o payload estiver fora do contrato, o Pydantic levantara erro de validacao com detalhes dos campos invalidos.
