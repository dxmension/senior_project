FROM python:3.12-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./
ENV UV_LINK_MODE=copy
RUN uv sync --frozen

COPY . .

CMD ["uv", "run", "uvicorn", "--app-dir", "src", "nutrack.main:app", "--host", "0.0.0.0", "--port", "8000"]
