FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LOGIAI_HOME=/app

WORKDIR /app

COPY requirements.txt /tmp/build/requirements.txt
COPY pyproject.toml README.md /tmp/build/
COPY logiai/ /tmp/build/logiai/

RUN pip install --no-cache-dir -r /tmp/build/requirements.txt \
    && pip install --no-cache-dir --no-deps /tmp/build \
    && rm -rf /tmp/build \
    && python -m logiai.dataset \
    && python -m logiai.train \
    && useradd --create-home --uid 10001 logiai \
    && chown -R logiai:logiai /app

USER logiai

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --retries=10 CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"]

CMD ["uvicorn", "logiai.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
