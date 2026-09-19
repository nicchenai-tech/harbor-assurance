FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HARBOR_PUBLIC_DEMO=1 \
    HARBOR_OCR_BACKEND=tesseract \
    HARBOR_DATA=/app/demo-data \
    HARBOR_RUNTIME=/tmp/harbor-runtime \
    PORT=8080

RUN apt-get update \
    && apt-get install -y --no-install-recommends tesseract-ocr curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml requirements-lock.txt ./
COPY harbor ./harbor
COPY web ./web
COPY demo-data ./demo-data
RUN pip install --no-cache-dir .

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 CMD curl -fsS http://127.0.0.1:${PORT}/api/health || exit 1
CMD ["python", "-m", "harbor.server"]
