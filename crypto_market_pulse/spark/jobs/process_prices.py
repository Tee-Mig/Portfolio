"""
PySpark job: Bronze Parquet → Silver PostgreSQL
Cleans price data and computes technical indicators.
"""
from __future__ import annotations

import argparse
import os

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window

POSTGRES_URL = os.getenv("POSTGRES_CONN", "jdbc:postgresql://postgres:5432/crypto_pulse")
POSTGRES_PROPS = {
    "user": os.getenv("POSTGRES_USER", "admin"),
    "password": os.getenv("POSTGRES_PASSWORD", "admin"),
    "driver": "org.postgresql.Driver",
}


def build_spark_session() -> SparkSession:
    return (
        SparkSession.builder.appName("ProcessCryptoPrices")
        .config("spark.jars", "/opt/extra-jars/postgresql-42.7.1.jar")
        .getOrCreate()
    )


def add_rsi(df, col_name: str = "pct_change_24h", window_size: int = 14):
    """Simplified RSI from percentage changes."""
    w = (
        Window.partitionBy("coin_id")
        .orderBy(F.col("ingestion_timestamp").cast("long"))
        .rowsBetween(-window_size, -1)
    )
    avg_gain = F.avg(F.when(F.col(col_name) > 0, F.col(col_name)).otherwise(0)).over(w)
    avg_loss = F.avg(F.when(F.col(col_name) < 0, F.abs(F.col(col_name))).otherwise(0)).over(w)
    rsi = F.when(avg_loss == 0, F.lit(100.0)).otherwise(
        100.0 - (100.0 / (1 + avg_gain / avg_loss))
    )
    return df.withColumn("avg_gain", avg_gain).withColumn("avg_loss", avg_loss).withColumn("rsi", rsi)


def main(date: str) -> None:
    spark = build_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    bronze_path = f"/opt/data/bronze/prices/{date.replace('-', '/')}/*/*.parquet"

    try:
        df = spark.read.parquet(bronze_path)
    except Exception as e:
        print(f"No data found for {date}: {e}")
        spark.stop()
        return

    df = df.dropDuplicates(["id", "ingestion_timestamp"])
    df = df.filter(F.col("current_price").isNotNull() & (F.col("current_price") > 0))

    df = df.select(
        F.col("id").alias("coin_id"),
        F.col("symbol"),
        F.col("name"),
        F.col("current_price").cast("double"),
        F.col("market_cap").cast("double"),
        F.col("total_volume").cast("double"),
        F.col("price_change_percentage_1h_in_currency").cast("double").alias("pct_change_1h"),
        F.col("price_change_percentage_24h_in_currency").cast("double").alias("pct_change_24h"),
        F.col("price_change_percentage_7d_in_currency").cast("double").alias("pct_change_7d"),
        F.col("high_24h").cast("double"),
        F.col("low_24h").cast("double"),
        F.to_timestamp("ingestion_timestamp").alias("ingestion_timestamp"),
        F.to_date(F.col("ingestion_timestamp")).alias("date"),
    )

    # Rolling 24h volatility (std of hourly % changes)
    w24h = (
        Window.partitionBy("coin_id")
        .orderBy(F.col("ingestion_timestamp").cast("long"))
        .rangeBetween(-24 * 3600, 0)
    )
    df = df.withColumn("volatility_24h", F.stddev("pct_change_1h").over(w24h))

    df = add_rsi(df)
    df = df.drop("avg_gain", "avg_loss")

    # Deduplicate to one row per coin per hour
    w_dedup = Window.partitionBy("coin_id", F.date_trunc("hour", F.col("ingestion_timestamp"))).orderBy(
        F.col("ingestion_timestamp").desc()
    )
    df = df.withColumn("_rn", F.row_number().over(w_dedup)).filter(F.col("_rn") == 1).drop("_rn")

    count = df.count()
    df.write.jdbc(url=POSTGRES_URL, table="silver.prices", mode="append", properties=POSTGRES_PROPS)
    print(f"Wrote {count} price records to silver.prices for {date}")
    spark.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="Processing date YYYY-MM-DD")
    args = parser.parse_args()
    main(args.date)
