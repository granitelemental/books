FROM python:3.8.1-slim

RUN pip install poetry==1.0.9

ADD web/poetry.lock  /
ADD web/pyproject.toml /

RUN poetry config virtualenvs.create false

RUN poetry install --no-dev --no-interaction --no-ansi -vvv

ADD web/.  /



CMD python web/main.py