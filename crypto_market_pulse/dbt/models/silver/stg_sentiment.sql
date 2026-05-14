{{ config(materialized='table', schema='silver') }}

with source as (
    select * from {{ source('silver', 'sentiment') }}
),

deduped as (
    select *,
           row_number() over (
               partition by coin_id, hour
               order by ingestion_timestamp desc
           ) as rn
    from source
),

enriched as (
    select
        coin_id,
        hour,
        date,
        avg_sentiment_score,
        fear_greed_value,
        value_classification,
        post_count,
        -- Rescale [0,1] → [-1,1] where 0.5 maps to 0
        round(((avg_sentiment_score - 0.5) * 2)::numeric, 4) as sentiment_index,
        case
            when avg_sentiment_score >= 0.6 then 'bullish'
            when avg_sentiment_score <= 0.4 then 'bearish'
            else 'neutral'
        end as sentiment_label,
        ingestion_timestamp
    from deduped
    where rn = 1
)

select * from enriched
