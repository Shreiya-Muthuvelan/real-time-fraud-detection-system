# Data Ingestion & Database Setup

This project uses a Dockerized PostgreSQL database and a Dockerized ingestion script to load the PaySim fraud detection dataset into a relational database. The goal of this step is to build the **Bronze (raw)** and **Silver (cleaned)** data layers for the fraud detection pipeline.

---

## Architecture Overview

```
PaySim CSV → Docker Ingestion Script → PostgreSQL (Raw Table)
                                                ↓
                                       SQL Transformations
                                                ↓
                                   Cleaned & Indexed Tables
```

---
## Step 0 — Create a Network
```bash
docker network create fin_network
```
## Step 1 — Run PostgreSQL Container

```bash
docker run -it --name fin_db \
  --network fin_network \
  -e POSTGRES_USER=root \
  -e POSTGRES_PASSWORD=root \
  -e POSTGRES_DB=fraud_db \
  -v data:/var/lib/postgresql \
  -p 5432:5432 \
  postgres:18
```

This container hosts the PostgreSQL database used to store transaction data.

---

## Step 2 — Build Ingestion Docker Image

```bash
docker build -t fraud_ingest:v001 .
```

This image contains the Python ingestion script that loads the CSV data into PostgreSQL. Needs to be run from the ingestion directory

---

## Step 3 — Run Data Ingestion

```bash
docker run -it \
  --network=fin_network \
  -v "${PWD}/data:/data" \
  fraud_ingest:v001 \
  --user=root \
  --password=root \
  --host=fin_db \
  --port=5432 \
  --db=fraud_db \
  --table_name=transactions \
  --csv_path=/data/paysim.csv
```

This loads the PaySim dataset into the `transactions` table in PostgreSQL.

---

## Step 4 — Connect to PostgreSQL

```bash
docker exec -it fin_db psql -U root -d fraud_db
```

Verify the data was loaded correctly:

```sql
\dt
SELECT COUNT(*) FROM transactions;
SELECT "isFraud", COUNT(*) FROM transactions GROUP BY "isFraud";
```

---

## Step 5 — Data Transformation (Staging → Clean Layer)

The transformation step produces a cleaned, indexed, analytics-ready table from the raw data. It performs the following operations:

- Rename columns to snake_case
- Add a primary key
- Create indexes for query performance
- Create a fraud-only subset table

### Output Tables

| Table | Description |
|---|---|
| `transactions` | Raw data (Bronze layer) |
| `transactions_clean` | Cleaned data (Silver layer) |
| `fraud_transactions` | Fraud-only transactions |

> These transformations are stored in `sql/create_tables.sql` and will later be automated using Airflow.

---

## SQL — `sql/create_tables.sql`

Create the file at `sql/create_tables.sql`:

```sql
-- Create cleaned transactions table
CREATE TABLE transactions_clean AS
SELECT
    "index",
    step,
    type,
    amount,
    "nameOrig"       AS sender,
    "oldbalanceOrg"  AS old_balance_orig,
    "newbalanceOrig" AS new_balance_orig,
    "nameDest"       AS receiver,
    "oldbalanceDest" AS old_balance_dest,
    "newbalanceDest" AS new_balance_dest,
    "isFraud"        AS is_fraud,
    "isFlaggedFraud" AS is_flagged_fraud
FROM transactions;

-- Add primary key
ALTER TABLE transactions_clean
ADD COLUMN transaction_id SERIAL PRIMARY KEY;

-- Create indexes
CREATE INDEX idx_sender   ON transactions_clean(sender);
CREATE INDEX idx_receiver ON transactions_clean(receiver);
CREATE INDEX idx_fraud    ON transactions_clean(is_fraud);

-- Create fraud-only table
CREATE TABLE fraud_transactions AS
SELECT *
FROM transactions_clean
WHERE is_fraud = 1;
```

> Airflow will execute this SQL file automatically after ingestion.

---

## Docker Compose — `docker-compose.yml`

Instead of running multiple `docker run` commands manually, use Docker Compose. Create `docker-compose.yml` in the project root:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:18
    container_name: fin_db
    environment:
      POSTGRES_USER: root
      POSTGRES_PASSWORD: root
      POSTGRES_DB: fraud_db
    volumes:
      - postgres_data:/var/lib/postgresql
    ports:
      - "5432:5432"
    networks:
      - fin_network

  ingest:
    build: .
    container_name: fraud_ingest
    depends_on:
      - postgres
    networks:
      - fin_network
    volumes:
      - ./data:/data
    command: >
      --user=root
      --password=root
      --host=fin_db
      --port=5432
      --db=fraud_db
      --table_name=transactions
      --csv_path=/data/paysim.csv

volumes:
  postgres_data:

networks:
  fin_network:
    driver: bridge
```

Then bring everything up with a single command:

```bash
docker-compose up
```

This will automatically:

1. Start the PostgreSQL container
2. Run the ingestion container
3. Load the PaySim data into the database

