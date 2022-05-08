# syntax=docker/dockerfile:1.2
FROM python:3.10-slim as base

ENV PIP_DISABLE_PIP_VERSION_CHECK=on \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPYCACHEPREFIX=/tmp \
    POETRY_VIRTUALENVS_CREATE=false \
    PIP_TRUSTED_HOST="pypi.org files.pythonhosted.org" \
    CURL_CA_BUNDLE=

RUN useradd -ms /bin/bash app && mkdir /app && chown -R app /app &&\
    apt update && apt -y install --no-install-recommends curl && \
    curl -kfsSL -o /usr/local/bin/dbmate https://github.com/amacneil/dbmate/releases/latest/download/dbmate-linux-amd64 && \
    chmod +x /usr/local/bin/dbmate && \
    apt remove -y --purge curl && \
    apt autoremove -y


WORKDIR /app


FROM base as builder

COPY poetry.lock pyproject.toml ./
RUN apt update && \
    apt -y install --no-install-recommends build-essential && \
    pip install -U pip poetry && \
    python -m venv /venv && \
    chown -R app /venv && \
    . /venv/bin/activate && \
    pip install -U pip wheel && \
    poetry install -E production --no-dev --no-root && \
    apt remove -y --purge curl && \
    apt autoremove -y && \
    rm -rf /root/.cache/pip

FROM base as prod

ENV PATH /venv/bin:$PATH

COPY --from=builder /venv /venv

COPY ./back ./back
COPY ./db ./db

USER app

CMD ["gunicorn",\
    "--access-logfile",\
    "-",\
    "--error-logfile",\
    "-",\
    "-k",\
    "uvicorn.workers.UvicornWorker",\
    "-w",\
    "1",\
    "-b",\
    "0.0.0.0:8000",\
    "back.app:app"]


