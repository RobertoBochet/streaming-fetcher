FROM python:3.13-slim AS compiler

WORKDIR /app

COPY . .

ENV PATH="/root/.local/bin:${PATH}"

RUN <<EORUN
set -e

apt update
apt install --no-install-recommends -y \
    curl \
    build-essential \
    pipx \
    git

pipx install poetry==2.2.1

poetry build --format wheel

EORUN

FROM python:3.13-slim

WORKDIR /app

COPY --from=compiler /app/dist/*.whl .

RUN <<EORUN
set -e

apt update
apt install --no-install-recommends -y  git ffmpeg

pip3 install --no-cache-dir -- *.whl
rm *.whl

playwright install --with-deps firefox

EORUN

ENV SB__BROWSER__TYPE="firefox"

ENTRYPOINT []
