FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml /app/pyproject.toml
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir .

COPY . /app

ENV PYTHONPATH=/app
EXPOSE 8002

CMD ["uvicorn", "app.main:app", "--app-dir", "/app/services/fl-orchestrator", "--host", "0.0.0.0", "--port", "8002"]
