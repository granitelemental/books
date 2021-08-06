FROM python:3.8.1-slim

RUN pip install poetry==1.0.9

ADD poetry.lock  /
ADD pyproject.toml /

RUN poetry config virtualenvs.create false

RUN poetry install --no-dev --no-interaction --no-ansi -vvv

ADD .  /



CMD python main.py