"""Test Harness do TaskAnalyzer (pytest).

Traduz os cenários de aceite da especificação:
    - Cenário 1: sucesso (métricas corretas);
    - Cenário 2: exceção (datas inconsistentes e entradas inválidas);
    - Casos de borda: entrada vazia e apenas tarefas pendentes.
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from task_analyzer import TaskValidationError, analyze_tasks  # noqa: E402

BASE = datetime(2026, 9, 1, 8, 0, tzinfo=timezone.utc)
AGORA = BASE + timedelta(hours=100)


def _tarefa(
    id_tarefa: int,
    prioridade: str,
    status: str,
    conclusao_h: float | None,
    prazo_h: float,
) -> dict[str, Any]:
    """Cria uma tarefa de teste com datas relativas a ``BASE`` (em horas)."""
    return {
        "id_tarefa": id_tarefa,
        "data_criacao": BASE,
        "data_conclusao": (
            BASE + timedelta(hours=conclusao_h) if conclusao_h is not None else None
        ),
        "prazo": BASE + timedelta(hours=prazo_h),
        "prioridade": prioridade,
        "status": status,
    }


@pytest.fixture
def tarefas_validas() -> list[dict[str, Any]]:
    """Conjunto de tarefas válidas com prioridades e status variados."""
    return [
        _tarefa(1, "alta", "concluído", 10, 12),
        _tarefa(2, "alta", "concluído", 30, 24),
        _tarefa(3, "média", "concluído", 5, 8),
        _tarefa(4, "baixa", "pendente", None, 200),
        _tarefa(5, "média", "pendente", None, 50),
        _tarefa(6, "baixa", "cancelado", None, 10),
    ]


# ---------------------------------------------------------------- Cenário 1
def test_cenario1_totais_gerais(tarefas_validas: list[dict[str, Any]]) -> None:
    """Dado tarefas válidas, os totais gerais devem estar corretos."""
    r = analyze_tasks(tarefas_validas, agora=AGORA)
    assert r["total_tarefas"] == 6
    assert r["total_concluidas"] == 3
    assert r["total_pendentes"] == 2


def test_cenario1_tempo_medio_geral(tarefas_validas: list[dict[str, Any]]) -> None:
    """O tempo médio geral deve ser (10 + 30 + 5) / 3 = 15.0 horas."""
    r = analyze_tasks(tarefas_validas, agora=AGORA)
    assert r["tempo_medio_conclusao_horas"] == 15.0


def test_cenario1_tempo_medio_por_prioridade(
    tarefas_validas: list[dict[str, Any]],
) -> None:
    """O tempo médio por prioridade deve ser calculado separadamente."""
    p = analyze_tasks(tarefas_validas, agora=AGORA)["indicadores_por_prioridade"]
    assert p["alta"]["tempo_medio_conclusao_horas"] == 20.0
    assert p["média"]["tempo_medio_conclusao_horas"] == 5.0
    assert p["baixa"]["tempo_medio_conclusao_horas"] == 0.0


def test_cenario1_taxa_atraso(tarefas_validas: list[dict[str, Any]]) -> None:
    """Atrasadas (tarefas 2 e 5) em 5 ativas = 40%; por prioridade também."""
    r = analyze_tasks(tarefas_validas, agora=AGORA)
    assert r["taxa_atraso_percentual"] == 40.0
    p = r["indicadores_por_prioridade"]
    assert p["alta"]["taxa_atraso_percentual"] == 50.0
    assert p["média"]["taxa_atraso_percentual"] == 50.0
    assert p["baixa"]["taxa_atraso_percentual"] == 0.0


def test_cenario1_totais_por_prioridade(
    tarefas_validas: list[dict[str, Any]],
) -> None:
    """Os totais devem ser agrupados corretamente por prioridade."""
    p = analyze_tasks(tarefas_validas, agora=AGORA)["indicadores_por_prioridade"]
    assert p["alta"]["total_tarefas"] == 2
    assert p["média"]["total_concluidas"] == 1
    assert p["média"]["total_pendentes"] == 1
    assert p["baixa"]["total_pendentes"] == 1


# ---------------------------------------------------------------- Cenário 2
def test_cenario2_conclusao_antes_da_criacao() -> None:
    """Dado data_conclusao < data_criacao, deve disparar TaskValidationError."""
    tarefa = _tarefa(1, "alta", "concluído", -5, 10)
    with pytest.raises(TaskValidationError, match="anterior"):
        analyze_tasks([tarefa], agora=AGORA)


def test_cenario2_concluida_sem_data_conclusao() -> None:
    """Tarefa concluída sem data_conclusao é inválida."""
    tarefa = _tarefa(1, "alta", "concluído", None, 10)
    with pytest.raises(TaskValidationError):
        analyze_tasks([tarefa], agora=AGORA)


@pytest.mark.parametrize(
    "campo, valor",
    [
        ("prioridade", "urgente"),
        ("status", "arquivado"),
        ("id_tarefa", 0),
        ("id_tarefa", "1"),
        ("prazo", "2026-09-01"),
        ("data_criacao", datetime(2026, 9, 1)),  # sem fuso horário
    ],
)
def test_cenario2_campos_invalidos(campo: str, valor: Any) -> None:
    """Valores fora do contrato devem disparar TaskValidationError."""
    tarefa = _tarefa(1, "alta", "pendente", None, 10)
    tarefa[campo] = valor
    with pytest.raises(TaskValidationError):
        analyze_tasks([tarefa], agora=AGORA)


def test_cenario2_campo_ausente() -> None:
    """Tarefa sem campo obrigatório deve disparar TaskValidationError."""
    tarefa = _tarefa(1, "alta", "pendente", None, 10)
    del tarefa["prazo"]
    with pytest.raises(TaskValidationError, match="prazo"):
        analyze_tasks([tarefa], agora=AGORA)


def test_cenario2_id_repetido() -> None:
    """Ids repetidos devem disparar TaskValidationError."""
    tarefas = [
        _tarefa(1, "alta", "pendente", None, 10),
        _tarefa(1, "baixa", "pendente", None, 10),
    ]
    with pytest.raises(TaskValidationError, match="repetido"):
        analyze_tasks(tarefas, agora=AGORA)


def test_cenario2_entrada_nao_e_lista() -> None:
    """Entrada que não é lista deve disparar TaskValidationError."""
    with pytest.raises(TaskValidationError):
        analyze_tasks("não é lista")  # type: ignore[arg-type]


# ------------------------------------------------------------ Casos de borda
def test_borda_entrada_vazia() -> None:
    """Entrada vazia retorna zeros, sem exceção e sem divisão por zero."""
    r = analyze_tasks([], agora=AGORA)
    assert r["total_tarefas"] == 0
    assert r["tempo_medio_conclusao_horas"] == 0.0
    assert r["taxa_atraso_percentual"] == 0.0
    assert r["indicadores_por_prioridade"]["alta"]["tempo_medio_conclusao_horas"] == 0.0


def test_borda_apenas_pendentes() -> None:
    """Só tarefas pendentes: tempo médio 0.0 e nenhuma exceção."""
    tarefas = [_tarefa(1, "alta", "pendente", None, 10)]
    r = analyze_tasks(tarefas, agora=AGORA)
    assert r["total_concluidas"] == 0
    assert r["total_pendentes"] == 1
    assert r["tempo_medio_conclusao_horas"] == 0.0


def test_borda_apenas_canceladas() -> None:
    """Só tarefas canceladas: métricas 0.0 (sem divisão por zero)."""
    tarefas = [_tarefa(1, "alta", "cancelado", None, 10)]
    r = analyze_tasks(tarefas, agora=AGORA)
    assert r["total_tarefas"] == 1
    assert r["taxa_atraso_percentual"] == 0.0


def test_borda_usa_horario_atual_por_padrao() -> None:
    """Sem 'agora', o horário atual é usado (prazo no passado = atrasada)."""
    tarefa = _tarefa(1, "alta", "pendente", None, 10)
    r = analyze_tasks([tarefa])
    assert r["taxa_atraso_percentual"] == 100.0
