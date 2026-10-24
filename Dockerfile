FROM python:3.14-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY pyproject.toml ./
COPY README.md ./

RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi --no-root

COPY src ./src

EXPOSE 8000

CMD ["uvicorn", "task_mgmt_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
