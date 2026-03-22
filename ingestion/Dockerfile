FROM python:3.11-slim

WORKDIR /app

COPY ingest_data.py .

RUN pip install pandas sqlalchemy psycopg2-binary tqdm

ENTRYPOINT ["python", "ingest_data.py"]