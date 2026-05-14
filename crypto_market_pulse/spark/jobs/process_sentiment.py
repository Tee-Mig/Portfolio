"""
PySpark job: Bronze Parquet → Silver PostgreSQL
Reads Fear & Greed Index entries and fans out one row per tracked coin per hour.
"""
from __future__ import annotations

import argparse
import os

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

POSTGRES_URL = os.getenv("POSTGRES_CONN", "jdbc:postgresql://postgres:5432/crypto_pulse")
POSTGRES_PROPS = {
    "user": os.getenv("POSTGRES_USER", "admin"),
    "password": os.getenv("POSTGRES_PASSWORD", "admin"),
    "driver": "org.postgresql.Driver",
}

COINS = ["bitcoin", "ethereum", "binancecoin", "solana"]


def build_spark_session() -> SparkSession:
    return (
        SparkSession.builder.appName("ProcessFearGreedSentiment")
        .config("spark.jars", "/opt/extra-jars/postgresql-42.7.1.jar")
        .getOrCreate()
    )


def main(date: str) -> None:
    spark = build_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    bronze_path = f"/opt/data/bronze/sentiment/{date.replace('-', '/')}/*/*.parquet"

    try:
        df = spark.read.parquet(bronze_path)
    except Exception as e:
        print(f"No data found for {date}: {e}")
        spark.stop()
        return

    df = df.dropDuplicates(["timestamp_unix"])

    df = df.withColumn(
        "hour",
        F.date_trunc("hour", F.from_unixtime(F.col("timestamp_unix").cast("long"))),
    )
    df = df.withColumn("date", F.to_date("hour"))
    df = df.withColumn("avg_sentiment_score", F.col("value") / F.lit(100.0))

    coins_df = spark.createDataFrame([(c,) for c in COINS], ["coin_id"])
    df = df.crossJoin(coins_df)

    result = df.select(
        "coin_id",
        "hour",
        "date",
        "avg_sentiment_score",
        F.col("value").alias("fear_greed_value"),
        "value_classification",
        F.lit(1).cast("long").alias("post_count"),
        "ingestion_timestamp",
    )

    count = result.count()
    result.write.jdbc(
        url=POSTGRES_URL, table="silver.sentiment", mode="append", properties=POSTGRES_PROPS
    )
    print(f"Wrote {count} sentiment records to silver.sentiment for {date}")
    spark.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="Processing date YYYY-MM-DD")
    args = parser.parse_args()
    main(args.date)
