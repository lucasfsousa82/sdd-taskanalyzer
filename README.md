# sdd-taskanalyzer

![CI](https://github.com/lucasfsousa82/sdd-taskanalyzer/actions/workflows/ci.yml/badge.svg)

Módulo **TaskAnalyzer**: analisa tarefas e calcula métricas de produtividade
(totais, tempo médio de conclusão em horas e taxa de atraso), no geral e por
prioridade. Projeto do Bootcamp III (UniCEUB), desenvolvido com
**Spec-Driven Development (SDD)**, código gerado por assistente de IA e
homologado por um humano.

**Autor:** Lucas Ferreira de Sousa

## Status do projeto

- Fase 1 — Especificação SDD e governança de contexto: concluída
- Fase 2 — Implementação com IA, Test Harness e versionamento: concluída
- Fase 3 — CI/CD (GitHub Actions), Docker e governança de IA: concluída

O selo **CI** acima mostra o resultado da última execução do pipeline na `main`.

## Estrutura

```
sdd-taskanalyzer/
├── .github/
│   └── workflows/
│       └── ci.yml                       # Pipeline de integração contínua
├── Dockerfile                           # Empacotamento (python:3.11-slim)
├── docker-compose.yml                   # Orquestração da suíte de testes
├── .dockerignore
├── .gitignore
├── CONTEXT_RULES.md                     # Regras de governança para a IA
├── README.md
├── requirements.txt                     # Dependências autorizadas (pytest)
├── specs/
│   ├── task_analyzer_spec.md            # Contrato SDD (v1.1)
│   ├── requirements.yaml                # Requisitos em formato de máquina
│   └── system_design_document.pdf       # Documento de design (PDF)
├── tests/
│   └── test_harness.py                  # Test Harness (pytest)
└── src/
    └── task_analyzer.py                 # Código gerado via IA e homologado
```

## Como executar localmente

Requer Python 3.11 ou superior.

```bash
python -m venv venv
venv\Scripts\activate          # Windows (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
python -m pytest -v
```

## Como executar com Docker

Requer Docker instalado. Não é necessário ter Python na máquina.

```bash
docker build -t sdd-taskanalyzer .
docker run --rm sdd-taskanalyzer
```

Ou, com o Docker Compose, em um único comando:

```bash
docker compose run --rm tests
```

Nos dois casos a suíte completa é executada em um ambiente isolado e o
resultado esperado é `20 passed`.

## Integração contínua (CI)

O workflow `.github/workflows/ci.yml` roda a cada push ou Pull Request nas
branches `main` e `develop`:

1. baixa o código;
2. configura o Python 3.11 em `ubuntu-latest`;
3. instala as dependências de `requirements.txt`;
4. executa `pytest tests/test_harness.py -v`.

## Fluxo de trabalho e governança

Branches `feature/*` são integradas à `main` por Pull Request, com revisão
humana contra as regras de `CONTEXT_RULES.md` antes do merge. Todo código
gerado por IA passa por: geração, barreira do contrato SDD, validação humana
e integração.

## Exemplo de uso

```python
from datetime import datetime, timezone
from src.task_analyzer import analyze_tasks

tarefas = [{
    "id_tarefa": 1,
    "data_criacao": datetime(2026, 9, 1, 8, 0, tzinfo=timezone.utc),
    "data_conclusao": datetime(2026, 9, 1, 18, 0, tzinfo=timezone.utc),
    "prazo": datetime(2026, 9, 1, 20, 0, tzinfo=timezone.utc),
    "prioridade": "alta",
    "status": "concluído",
}]
print(analyze_tasks(tarefas)["tempo_medio_conclusao_horas"])  # 10.0
```
