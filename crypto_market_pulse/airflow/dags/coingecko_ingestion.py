from __future__ import annotations

import os
from datetime import datetime, timedelta

import pandas as pd
import requests
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

COINS = ["bitcoin", "ethereum", "binancecoin", "solana"]
BRONZE_PATH = "/opt/data/bronze/prices"

default_args = {
    "owner": "airflow",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
}


def fetch_coingecko_prices(**context) -> str:
    api_key = os.getenv("COINGECKO_API_KEY", "")
    headers = {"x-cg-demo-api-key": api_key} if api_key else {}

    params = {
        "vs_currency": "usd",
        "ids": ",".join(COINS),
        "order": "market_cap_desc",
        "per_page": 10,
        "page": 1,
        "sparkline": False,
        "price_change_percentage": "1h,24h,7d",
    }
    resp = requests.get(
        "https://api.coingecko.com/api/v3/coins/markets",
        params=params,
        headers=headers,
        timeout=30,
    )
    resp.raise_for_status()

    logical_date = context["logical_date"]
    date_str = logical_date.strftime("%Y/%m/%d")
    hour_str = logical_date.strftime("%H")
    output_dir = f"{BRONZE_PATH}/{date_str}/{hour_str}"
    os.makedirs(output_dir, exist_ok=True)

    df = pd.DataFrame(resp.json())
    df["ingestion_timestamp"] = logical_date.isoformat()

    output_path = f"{output_dir}/prices_{logical_date.strftime('%Y%m%d_%H%M%S')}.parquet"
    df.to_parquet(output_path, index=False)
    print(f"Saved {len(df)} rows → {output_path}")
    return output_path


with DAG(
    dag_id="coingecko_ingestion",
    default_args=default_args,
    description="Fetch crypto prices from CoinGecko every hour",
    schedule="@hourly",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["ingestion", "coingecko", "bronze"],
) as dag:

    fetch_prices = PythonOperator(
        task_id="fetch_prices",
        python_callable=fetch_coingecko_prices,
    )

    process_prices = BashOperator(
        task_id="process_prices",
        bash_command=(
            "unset SPARK_MASTER && spark-submit "
            "--master local[2] "
            "--jars /opt/extra-jars/postgresql-42.7.1.jar "
            "--driver-memory 1g "
            "/opt/spark/jobs/process_prices.py "
            "--date {{ ds }}"
        ),
    )

    run_dbt = BashOperator(
        task_id="run_dbt",
        bash_command=(
            "cd /opt/dbt && "
            "dbt run --profiles-dir . --select silver.stg_prices gold "
            "--vars '{\"run_date\": \"{{ ds }}\"}'"
        ),
    )

    fetch_prices >> process_prices >> run_dbt
