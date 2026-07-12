# syntax=docker/dockerfile:1.7
FROM python:3.11-alpine

ARG MODEL_REVISION=7dabda4d13d513e3e842b20f0d435c732f172cbe
ARG MODEL_URL=https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/7dabda4d13d513e3e842b20f0d435c732f172cbe/qwen2.5-3b-instruct-q4_k_m.gguf
ARG MODEL_SHA256=626b4a6678b86442240e33df819e00132d3ba7dddfe1cdc4fbb18e0a9615c62d

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src \
    MODEL_PATH=/app/models/qwen2.5-3b-instruct-q4_k_m.gguf \
    INPUT_PATH=/input/tasks.json \
    OUTPUT_PATH=/output/results.json \
    ROUTING_PROFILE=hybrid \
    LOCAL_THREADS=2 \
    LOCAL_CONTEXT=4096 \
    REMOTE_WORKERS=3

WORKDIR /app

RUN apk add --no-cache ca-certificates curl libgomp libstdc++

COPY requirements-runtime.txt ./
RUN pip install --no-cache-dir -r requirements-runtime.txt

RUN --mount=type=cache,id=qwen25-3b-gguf,target=/model-cache \
    mkdir -p /app/models \
    && touch /model-cache/model.gguf \
    && (echo "$MODEL_SHA256  /model-cache/model.gguf" | sha256sum -c - >/dev/null 2>&1 \
        || curl --http1.1 --fail --location \
            --retry 10 --retry-all-errors --retry-delay 2 \
            --continue-at - --output /model-cache/model.gguf "$MODEL_URL") \
    && echo "$MODEL_SHA256  /model-cache/model.gguf" | sha256sum -c - \
    && cp /model-cache/model.gguf "$MODEL_PATH"

COPY src ./src
COPY LICENSE README.md ./

CMD ["python", "-m", "tokenrouter.agent"]
