FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
        tesseract-ocr \
        tesseract-ocr-eng \
        tesseract-ocr-rus \
        tesseract-ocr-kaz \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --system app && useradd --system --create-home --gid app app
RUN pip install uv

COPY pyproject.toml uv.lock ./
ENV UV_LINK_MODE=copy
RUN uv sync --frozen

COPY . .
RUN mkdir -p /tmp/material_uploads && chown -R app:app /app /tmp/material_uploads

USER app

CMD ["uv", "run", "uvicorn", "--app-dir", "src", "nutrack.main:app", "--host", "0.0.0.0", "--port", "8000"]
