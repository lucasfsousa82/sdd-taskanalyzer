# Imagem base leve, na versão mínima exigida pelas CONTEXT_RULES (Python 3.11+)
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependências primeiro, para aproveitar o cache de camadas do Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código da aplicação e suíte de testes
COPY src/ ./src/
COPY tests/ ./tests/

# Comando padrão: executar o Test Harness
CMD ["pytest", "tests/test_harness.py", "-v"]
