# sdd-taskanalyzer

Módulo **TaskAnalyzer**: analisa tarefas e calcula métricas de produtividade
(totais, tempo médio de conclusão em horas e taxa de atraso), no geral e por
prioridade. Projeto do Bootcamp III (UniCEUB), desenvolvido com
**Spec-Driven Development (SDD)** e código gerado por assistente de IA,
homologado por um humano.

**Autor:** Lucas Ferreira de Sousa

## Status do build

- Fase 1 — Especificação SDD: concluída
- Fase 2 — Implementação, testes e versionamento: concluída (20 testes, 100% aprovados)
- Fase 3 — CI/CD e Docker: pendente

## Estrutura

```
sdd-taskanalyzer/
├── README.md
├── CONTEXT_RULES.md          # Regras de governança para a IA
├── .gitignore
├── requirements.txt          # Dependências autorizadas (pytest)
├── specs/
│   └── task_analyzer_spec.md # Contrato SDD
├── tests/
│   └── test_harness.py       # Testes automatizados (pytest)
└── src/
    └── task_analyzer.py      # Código gerado via IA e homologado
```

## Como executar

Requer Python 3.11+.

```bash
python -m venv venv
venv\Scripts\activate          # Windows (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
python -m pytest -v
```

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

## Fluxo de trabalho

Branches `feature/*` integradas à `main` por Pull Request, com revisão humana
contra as `CONTEXT_RULES.md` antes do merge.
