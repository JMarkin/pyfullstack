# syntax=docker/dockerfile:1.2
FROM node:17-slim

ENV NODE_TLS_REJECT_UNAUTHORIZED 0
RUN apt update && \
    apt install -y --no-install-recommends build-essential python3-dev
WORKDIR  /app

RUN npm config set prefix /node_modules && \
    npm config set strict-ssl false

COPY ./front/package.json .

RUN npm install

USER node
