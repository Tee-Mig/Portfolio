from __future__ import annotations

import os
from datetime import datetime, timedelta

import pandas as pd
import requests
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

BRONZE_PATH = "/opt/data/bronze/sentiment"
FNG_API_URL = "https://api.alternative.me/fng/"

default_args = {
    "owner": "airflow",
    "retries": 3,
    "retry_delay": timedelta(minutes=10),
    "email_on_failure": False,
}


def fetch_fear_greed(**context) -> str:
    resp = requests.get(FNG_API_URL, params={"limit": 2, "format": "json"}, timeout=30)
    resp.raise_for_status()
    entries = resp.json()["data"]

    logical_date = context["logical_date"]
    records = [
        {
            "value": int(e["value"]),
            "value_classification": e["value_classification"],
            "timestamp_unix": int(e["timestamp"]),
            "ingestion_timestamp": logical_date.isoformat(),
        }
        for e in entries
    ]

    date_str = logical_date.strftime("%Y/%m/%d")
    hour_str = logical_date.strftime("%H")
    output_dir = f"{BRONZE_PATH}/{date_str}/{hour_str}"
    os.makedirs(output_dir, exist_ok=True)

    df = pd.DataFrame(records)
    output_path = f"{output_dir}/fng_{logical_date.strftime('%Y%m%d_%H%M%S')}.parquet"
    df.to_parquet(output_path, index=False)
    print(f"Saved {len(df)} Fear & Greed entries → {output_path}")
    return output_path


with DAG(
    dag_id="sentiment_ingestion",
    default_args=default_args,
    description="Fetch Fear & Greed Index from alternative.me every 6 hours",
    schedule="0 */6 * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["ingestion", "sentiment", "bronze"],
) as dag:

    fetch_fng = PythonOperator(
        task_id="fetch_fear_greed",
        python_callable=fetch_fear_greed,
    )

    process_sentiment = BashOperator(
        task_id="process_sentiment",
        bash_command=(
            "unset SPARK_MASTER && spark-submit "
            "--master local[2] "
            "--jars /opt/extra-jars/postgresql-42.7.1.jar "
            "--driver-memory 1g "
            "/opt/spark/jobs/process_sentiment.py "
            "--date {{ ds }}"
        ),
    )

    run_dbt = BashOperator(
        task_id="run_dbt",
        bash_command=(
            "cd /opt/dbt && "
            "dbt run --profiles-dir . --select silver.stg_sentiment gold "
            "--vars '{\"run_date\": \"{{ ds }}\"}'"
        ),
    )

    fetch_fng >> process_sentiment >> run_dbt
