FROM ghcr.io/astral-sh/uv:debian-slim

WORKDIR /app

COPY pyproject.toml uv.lock /app/

RUN uv sync --locked

COPY . /app/

EXPOSE 8000

CMD ["sh", "-c", "uv run python -m app.db.create_db && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
