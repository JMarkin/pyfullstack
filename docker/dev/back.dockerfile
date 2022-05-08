# syntax=docker/dockerfile:1.2
FROM python:3.10-slim

ENV PIP_DISABLE_PIP_VERSION_CHECK=on \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPYCACHEPREFIX=/tmp \
    POETRY_VIRTUALENVS_CREATE=false \
    PIP_TRUSTED_HOST="pypi.org files.pythonhosted.org" \
    CURL_CA_BUNDLE=


RUN mkdir -p /app && \
    useradd -ms /bin/bash app && \
    chmod -R 777 /app

WORKDIR /app

RUN apt update && \
    apt install -y --no-install-recommends curl vim git build-essential && \
    curl -kfsSL -o /usr/local/bin/dbmate https://github.com/amacneil/dbmate/releases/latest/download/dbmate-linux-amd64 && \
    chmod +x /usr/local/bin/dbmate

RUN pip install -U pip &&\
    pip install poetry

COPY ./pyproject.toml ./poetry.lock ./

RUN poetry install --no-root

USER app
