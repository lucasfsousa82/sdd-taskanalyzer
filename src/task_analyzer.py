"""Módulo TaskAnalyzer.

Analisa uma lista de tarefas e calcula métricas de produtividade: totais,
tempo médio de conclusão (em horas) e taxa de atraso (em %), no geral e por
prioridade. Segue o contrato definido em ``specs/task_analyzer_spec.md``.
"""

import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

PRIORIDADES: tuple[str, ...] = ("baixa", "média", "alta")
STATUS_VALIDOS: tuple[str, ...] = ("concluído", "pendente", "cancelado")
CAMPOS_OBRIGATORIOS: tuple[str, ...] = (
    "id_tarefa",
    "data_criacao",
    "prazo",
    "prioridade",
    "status",
)


class TaskValidationError(Exception):
    """Erro disparado quando os dados de entrada violam o contrato."""


def _validar_data(valor: Any, campo: str, id_tarefa: Any) -> datetime:
    """Valida que o valor é um datetime com fuso horário e converte para UTC.

    Args:
        valor: Valor recebido para o campo de data.
        campo: Nome do campo (usado na mensagem de erro).
        id_tarefa: Identificador da tarefa (usado na mensagem de erro).

    Returns:
        O datetime convertido para UTC.

    Raises:
        TaskValidationError: Se não for datetime ou não tiver fuso horário.
    """
    if not isinstance(valor, datetime):
        raise TaskValidationError(
            f"Tarefa {id_tarefa}: o campo '{campo}' deve ser um datetime."
        )
    if valor.tzinfo is None:
        raise TaskValidationError(
            f"Tarefa {id_tarefa}: o campo '{campo}' deve ter fuso horário (UTC)."
        )
    return valor.astimezone(timezone.utc)


def _validar_tarefa(tarefa: dict[str, Any]) -> dict[str, Any]:
    """Valida uma tarefa e devolve uma cópia normalizada (datas em UTC).

    Args:
        tarefa: Dicionário com os campos da tarefa.

    Returns:
        Dicionário validado, com datas convertidas para UTC.

    Raises:
        TaskValidationError: Se algum campo estiver ausente ou inválido.
    """
    if not isinstance(tarefa, dict):
        raise TaskValidationError("Cada tarefa deve ser um dicionário.")

    for campo in CAMPOS_OBRIGATORIOS:
        if campo not in tarefa:
            raise TaskValidationError(f"Campo obrigatório ausente: '{campo}'.")

    id_tarefa = tarefa["id_tarefa"]
    if isinstance(id_tarefa, bool) or not isinstance(id_tarefa, int) or id_tarefa <= 0:
        raise TaskValidationError("'id_tarefa' deve ser um inteiro maior que zero.")
    if tarefa["prioridade"] not in PRIORIDADES:
        raise TaskValidationError(
            f"Tarefa {id_tarefa}: prioridade inválida '{tarefa['prioridade']}'."
        )
    if tarefa["status"] not in STATUS_VALIDOS:
        raise TaskValidationError(
            f"Tarefa {id_tarefa}: status inválido '{tarefa['status']}'."
        )

    validada: dict[str, Any] = {
        "id_tarefa": id_tarefa,
        "prioridade": tarefa["prioridade"],
        "status": tarefa["status"],
        "data_criacao": _validar_data(tarefa["data_criacao"], "data_criacao", id_tarefa),
        "prazo": _validar_data(tarefa["prazo"], "prazo", id_tarefa),
        "data_conclusao": None,
    }

    if tarefa["status"] == "concluído":
        if tarefa.get("data_conclusao") is None:
            raise TaskValidationError(
                f"Tarefa {id_tarefa}: tarefa concluída exige 'data_conclusao'."
            )
        conclusao = _validar_data(tarefa["data_conclusao"], "data_conclusao", id_tarefa)
        if conclusao < validada["data_criacao"]:
            raise TaskValidationError(
                f"Tarefa {id_tarefa}: 'data_conclusao' anterior a 'data_criacao'."
            )
        validada["data_conclusao"] = conclusao

    return validada


def _esta_atrasada(tarefa: dict[str, Any], agora: datetime) -> bool:
    """Indica se uma tarefa (não cancelada) está atrasada.

    Args:
        tarefa: Tarefa já validada.
        agora: Instante de referência, usado para tarefas pendentes.

    Returns:
        True se concluída após o prazo ou pendente com prazo vencido.
    """
    if tarefa["status"] == "concluído":
        return tarefa["data_conclusao"] > tarefa["prazo"]
    return agora > tarefa["prazo"]


def _calcular_metricas(tarefas: list[dict[str, Any]], agora: datetime) -> dict[str, Any]:
    """Calcula as métricas de um grupo de tarefas já validadas.

    Args:
        tarefas: Lista de tarefas validadas.
        agora: Instante de referência para tarefas pendentes.

    Returns:
        Dicionário com totais, tempo médio (horas) e taxa de atraso (%).
    """
    concluidas = [t for t in tarefas if t["status"] == "concluído"]
    pendentes = [t for t in tarefas if t["status"] == "pendente"]
    ativas = concluidas + pendentes

    tempo_medio = 0.0
    if concluidas:
        total_horas = sum(
            (t["data_conclusao"] - t["data_criacao"]).total_seconds() / 3600
            for t in concluidas
        )
        tempo_medio = round(total_horas / len(concluidas), 2)

    taxa_atraso = 0.0
    if ativas:
        atrasadas = sum(1 for t in ativas if _esta_atrasada(t, agora))
        taxa_atraso = round(atrasadas / len(ativas) * 100, 2)

    return {
        "total_tarefas": len(tarefas),
        "total_concluidas": len(concluidas),
        "total_pendentes": len(pendentes),
        "tempo_medio_conclusao_horas": tempo_medio,
        "taxa_atraso_percentual": taxa_atraso,
    }


def analyze_tasks(
    tasks: list[dict[str, Any]], agora: datetime | None = None
) -> dict[str, Any]:
    """Analisa uma lista de tarefas e retorna métricas de produtividade.

    Args:
        tasks: Lista de dicionários, um por tarefa, conforme o contrato.
        agora: Instante de referência para avaliar atraso de tarefas
            pendentes. Se omitido, usa o horário atual em UTC.

    Returns:
        Dicionário com as métricas gerais e, em ``indicadores_por_prioridade``,
        as mesmas métricas para cada prioridade.

    Raises:
        TaskValidationError: Se a entrada for inválida (campos ausentes,
            valores fora do contrato, datas inconsistentes ou ids repetidos).
    """
    if not isinstance(tasks, list):
        raise TaskValidationError("A entrada deve ser uma lista de tarefas.")

    referencia = agora if agora is not None else datetime.now(timezone.utc)
    if referencia.tzinfo is None:
        raise TaskValidationError("'agora' deve ter fuso horário (UTC).")
    referencia = referencia.astimezone(timezone.utc)

    logger.info("Analisando %d tarefa(s).", len(tasks))

    validadas: list[dict[str, Any]] = []
    ids_vistos: set[int] = set()
    for tarefa in tasks:
        validada = _validar_tarefa(tarefa)
        if validada["id_tarefa"] in ids_vistos:
            raise TaskValidationError(
                f"id_tarefa repetido: {validada['id_tarefa']}."
            )
        ids_vistos.add(validada["id_tarefa"])
        validadas.append(validada)

    resultado = _calcular_metricas(validadas, referencia)
    resultado["indicadores_por_prioridade"] = {
        prioridade: _calcular_metricas(
            [t for t in validadas if t["prioridade"] == prioridade], referencia
        )
        for prioridade in PRIORIDADES
    }
    logger.info("Análise concluída.")
    return resultado
