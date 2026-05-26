FROM python:3.12.11-slim

RUN pip install uv

WORKDIR /app

COPY pyproject.toml .

RUN uv pip install --system .

COPY . .

CMD ["python", "src/main.py"]
