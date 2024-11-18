FROM python:3.12-slim

ENV POETRY_VERSION=1.8.4 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

WORKDIR /app

RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

COPY data/ data/
COPY src/ src/
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

EXPOSE 8501 8502
CMD ["sh", "/app/start.sh"]
