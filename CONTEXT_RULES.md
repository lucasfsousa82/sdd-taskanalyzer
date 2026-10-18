# CONTEXT_RULES — Regras de Governança para Agentes de IA

Regras rígidas fornecidas ao assistente de IA para garantir alinhamento,
consistência e qualidade do código gerado no projeto **TaskAnalyzer**.
Fonte de verdade junto com `specs/task_analyzer_spec.md`.

## 1. Diretrizes Arquiteturais (obrigatórias)

- Python 3.11+ como versão mínima.
- Type hints em todas as funções e métodos (100%).
- Princípio Single Responsibility (SRP) e código limpo (PEP 8).
- Documentação no padrão Google style docstrings (módulos, classes, funções).
- Funções pequenas, coesas e com um único propósito.
- Tratamento de exceções específico, com mensagens claras.
- Logs estruturados com o módulo padrão `logging`.
- Código legível, manutenível, com nomes descritivos.

## 2. Proibições Explícitas

- Não utilizar bibliotecas externas não autorizadas (apenas biblioteca padrão e `pytest`).
- Não alterar, remover ou adaptar os cenários de teste fornecidos.
- Não modificar a estrutura de pastas definida na especificação.
- Não persistir dados em arquivos ou bancos de dados.
- Não alterar a assinatura (nome e parâmetros) das funções públicas sem autorização.
- Não gerar código sem testes correspondentes para as novas funcionalidades.
- Não inserir código duplicado ou desnecessário.
- Não assumir comportamentos não especificados no contrato de negócio.

## 3. Regras de Interação com IA

- Fornecer sempre o contexto completo (contrato, cenários e proibições) antes de pedir código.
- Validar se a IA compreendeu o contrato antes de aceitar a solução.
- Pedir explicações quando houver dúvida sobre a solução.
- Revisar criticamente todo código gerado (homologação humana).
- Rejeitar respostas que violem as proibições ou o contrato.
