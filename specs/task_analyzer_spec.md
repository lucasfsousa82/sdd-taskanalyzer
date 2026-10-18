# Especificação SDD — TaskAnalyzer (v1.1)

Transposta da Fase 1 (Google Docs). A v1.1 ajusta dois pontos para alinhar o
contrato ao Test Harness da Fase 2: o tempo é medido em **horas** e é calculado
a partir de `data_criacao`.

## 1. Propósito

Analisar tarefas e gerar métricas de produtividade: totais, tempo médio de
conclusão e taxa de atraso, no geral e por prioridade (baixa, média, alta).

## 2. Contrato de interface

Função pública: `analyze_tasks(tasks, agora=None) -> dict`
Exceção pública: `TaskValidationError`

### 2.1 Entradas (cada tarefa é um `dict`)

| Campo | Tipo | Obrigatório | Restrições |
|---|---|---|---|
| id_tarefa | int | Sim | Inteiro > 0 e único na lista |
| data_criacao | datetime | Sim | Com fuso horário (convertido para UTC) |
| data_conclusao | datetime | Só se concluída | Com fuso; não pode ser anterior a `data_criacao` |
| prazo | datetime | Sim | Com fuso horário |
| prioridade | str | Sim | "baixa", "média" ou "alta" |
| status | str | Sim | "concluído", "pendente" ou "cancelado" |

`agora` (opcional): instante de referência para avaliar atraso de pendentes;
padrão = horário atual em UTC.

### 2.2 Saídas (`dict`)

| Campo | Tipo | Descrição |
|---|---|---|
| total_tarefas | int | Todas as tarefas (inclui canceladas) |
| total_concluidas | int | Tarefas com status "concluído" |
| total_pendentes | int | Tarefas com status "pendente" |
| tempo_medio_conclusao_horas | float | Média de (`data_conclusao` − `data_criacao`) das concluídas, em horas, 2 casas decimais |
| taxa_atraso_percentual | float | % de tarefas atrasadas entre concluídas + pendentes, 2 casas decimais |
| indicadores_por_prioridade | dict | As mesmas 5 métricas para cada prioridade ("baixa", "média", "alta") |

### 2.3 Regras de negócio

1. Tempo médio considera apenas tarefas concluídas.
2. Atrasada = concluída com `data_conclusao` > `prazo`, ou pendente com `agora` > `prazo`.
3. Tarefas canceladas entram em `total_tarefas`, mas não na taxa de atraso.
4. Sem tarefas concluídas, o tempo médio é `0.0`; sem tarefas ativas, a taxa de atraso é `0.0` (sem divisão por zero).
5. Entrada vazia retorna todas as métricas zeradas, sem exceção.
6. Entradas inválidas disparam `TaskValidationError` com mensagem clara.

## 3. Cenários de aceite

**Cenário 1 — Sucesso.** Dado um conjunto de tarefas válidas, quando o
analisador for executado, então retorna `total_tarefas`, `total_concluidas`,
`total_pendentes`, `tempo_medio_conclusao_horas` (geral e por prioridade) e
`taxa_atraso_percentual` corretos.

**Cenário 2 — Exceção.** Dado uma entrada com datas inconsistentes
(`data_conclusao` < `data_criacao`) ou campos inválidos, quando o analisador for
executado, então dispara `TaskValidationError`.

**Casos de borda.** Entrada vazia ou só com tarefas pendentes retorna `0.0` nas
médias, sem exceções não tratadas.
