FROM python:3.12-slim

WORKDIR /src

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV POETRY_VENV=poetry_venv
RUN python3 -m venv $POETRY_VENV && $POETRY_VENV/bin/pip install poetry==1.8.4

COPY pyproject.toml poetry.lock ./

RUN $POETRY_VENV/bin/poetry config virtualenvs.create false \
	&& $POETRY_VENV/bin/poetry install --no-interaction --no-root \
	&& rm -rf $POETRY_VENV

COPY src/app ./app/

CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "app.main:app"]
