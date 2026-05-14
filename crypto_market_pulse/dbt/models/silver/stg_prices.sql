{{ config(materialized='table', schema='silver') }}

with source as (
    select * from {{ source('silver', 'prices') }}
),

deduped as (
    select *,
           row_number() over (
               partition by coin_id, date_trunc('hour', ingestion_timestamp)
               order by ingestion_timestamp desc
           ) as rn
    from source
)

select
    coin_id,
    symbol,
    name,
    current_price,
    market_cap,
    total_volume,
    pct_change_1h,
    pct_change_24h,
    pct_change_7d,
    high_24h,
    low_24h,
    coalesce(volatility_24h, 0)  as volatility_24h,
    coalesce(rsi, 50)            as rsi,
    date_trunc('hour', ingestion_timestamp) as hour,
    date,
    ingestion_timestamp
from deduped
where rn = 1
