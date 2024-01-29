FROM python:3.11-slim-bookworm

WORKDIR /app

ENV POETRY_VIRTUALENVS_CREATE false
COPY poetry.lock pyproject.toml ./
RUN pip install poetry && poetry install --without dev --all-extras --no-root --no-interaction --no-ansi

COPY . .

ENTRYPOINT ["python", "main.py"]
