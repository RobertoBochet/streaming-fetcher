FROM python:3.12-bookworm AS compiler

RUN apt update \
    && apt install --no-install-recommends -y \
        curl \
        build-essential \
        pipx \
        git

ENV PATH="/root/.local/bin:${PATH}"

RUN pipx install poetry==1.8.4

WORKDIR /app

COPY . .

RUN poetry build --format wheel


FROM python:3.12-slim

RUN apt update \
    && apt install --no-install-recommends -y \
        git \
        ffmpeg

WORKDIR /app

COPY --from=compiler /app/dist/*.whl .

RUN pip3 install --no-cache-dir -- *.whl

RUN rm *.whl

RUN playwright install --with-deps firefox

ENV SB__BROWSER__TYPE="firefox"

ENTRYPOINT []
