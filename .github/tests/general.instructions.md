---
applyTo: "tests/**/*, services/**/tests/**/*"
---
# Escopo: Testes Automatizados
Esta pasta contém a suíte de testes.

* Stack: Pytest.
* Nomenclatura: Para o nome do agrupamento de testes (ou classe), utilize o padrão `NomeDaClasse.nomeDoMetodo`.
* Nomenclatura de Métodos: Para os nomes dos métodos de teste, inicie sempre com a palavra `Deve`. Exemplo: `test_DeveRetornarErroQuandoFormatoInvalido`.
* Foco: Priorize testes unitários de regras de negócio, validações de schema e os testes de contrato dos endpoints REST.