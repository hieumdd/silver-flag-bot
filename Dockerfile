FROM python:3.11-slim-bookworm as builder

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

ENV PIP_NO_CACHE_DIR=off
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_DEFAULT_TIMEOUT=100

ENV POETRY_VIRTUALENVS_IN_PROJECT true

WORKDIR /app
COPY poetry.lock pyproject.toml ./
RUN pip install poetry && poetry install --without dev --all-extras --no-interaction --no-ansi

# 

FROM python:3.11-slim-bookworm as production
COPY --from=builder /app /app
WORKDIR /app
COPY . .
ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["python", "main.py"]
