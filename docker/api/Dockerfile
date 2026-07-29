FROM python:3.11-slim

WORKDIR /app

# Заменили psycopg2-binary на asyncpg
RUN pip install --no-cache-dir fastapi uvicorn sqlalchemy aiofiles qdrant-client python-multipart httpx asyncpg

COPY main.py .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]