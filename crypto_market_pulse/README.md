# Crypto Market Pulse

**End-to-end data pipeline** to analyze cryptocurrencies in near real-time

> Key question here: **does market sentiment predict crypto price movements?**

---

## What it does

Every hour, the pipeline collects BTC, ETH, BNB and SOL prices (CoinGecko) along with the Fear & Greed Index (sentiment indicator). Data is transformed to compute technical indicators (RSI, volatility), modeled in Bronze → Silver → Gold layers, then visualized in an interactive dashboard

---

## Stack

Apache Airflow · PySpark · dbt · PostgreSQL · Streamlit · Docker Compose

---

## How it works

Airflow runs two DAGs on a schedule: one hourly for crypto prices, one every 6 hours for the Fear & Greed Index. Raw data lands in Parquet files (Bronze), PySpark processes it and loads enriched tables into PostgreSQL (Silver), then dbt builds aggregated KPI models on top (Gold). The Streamlit dashboard reads from the Gold layer and refreshes after each pipeline run

---

## Requirements

- Docker Desktop
- `make` available (Git Bash / WSL on Windows)

---

## Installation

```bash
make setup     -> first-time setup
make rebuild   -> build and start all services
make init      -> run once after the first build
```

Then open http://localhost:8080 (admin / admin), enable both DAGs and trigger them. The dashboard at http://localhost:8501 updates automatically.

---

## Makefile commands

```
make setup          -> Create .env and download the JDBC driver
make init           -> Initialize Airflow database (once only)
make up             -> Start containers
make down           -> Stop and remove containers
make rebuild        -> Rebuild images + start
make restart        -> Restart containers
make ps             -> Container status
make logs           -> Follow all logs in real time
make logs-airflow   -> Airflow scheduler logs
make logs-spark     -> Spark master logs
make logs-dashboard -> Streamlit dashboard logs
make dbt-run        -> Run all dbt models
make dbt-test       -> Run dbt tests
make clean          -> Remove containers and volumes (full reset)
make urls           -> Print service URLs
```

---

## Interfaces

```
Airflow   -> http://localhost:8080  (admin / admin)
Spark UI  -> http://localhost:8082
Dashboard -> http://localhost:8501
```

---

## Structure

```
crypto-market-pulse/
├── airflow/
│   ├── dags/
│   │   ├── coingecko_ingestion.py   # CoinGecko prices → Bronze → PySpark → dbt
│   │   └── reddit_ingestion.py      # Fear & Greed → Bronze → PySpark → dbt
│   └── requirements.txt
├── spark/
│   ├── jobs/
│   │   ├── process_prices.py        # RSI + volatility → silver.prices
│   │   └── process_sentiment.py     # normalization → silver.sentiment
│   └── jars/                        # PostgreSQL JDBC driver (gitignored)
├── dbt/
│   ├── models/
│   │   ├── silver/                  # stg_prices, stg_sentiment
│   │   └── gold/                    # kpi_daily_summary, kpi_correlation, kpi_top_movers
│   └── macros/
├── dashboard/
│   └── app.py                       # Streamlit 3 pages
├── scripts/
│   ├── init-db.sh                   # DB + silver/gold schema creation
│   └── download-jars.sh             # JDBC driver download
├── Makefile
├── Dockerfile.airflow               # custom image: Airflow + Java + PySpark + dbt
├── docker-compose.yml
└── .env.example
```
