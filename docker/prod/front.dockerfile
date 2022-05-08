# syntax=docker/dockerfile:1.2
FROM node:17-slim as front

ENV NODE_TLS_REJECT_UNAUTHORIZED 0
RUN apt update && \
    apt install -y --no-install-recommends build-essential python3-dev
WORKDIR  /app

RUN npm config set prefix /node_modules && \
    npm config set strict-ssl false

COPY ./front .

RUN npm install
RUN npm run build


FROM nginx:alpine as prod

COPY --from=front /app/dist /var/www/
COPY ./nginx/prod.conf /etc/nginx/nginx.conf
