{{ config(materialized='table', schema='gold') }}

with prices as (
    select * from {{ ref('stg_prices') }}
),

sentiment as (
    select * from {{ ref('stg_sentiment') }}
),

daily_prices as (
    select
        coin_id,
        symbol,
        name,
        date,
        round(avg(current_price)::numeric, 4)     as avg_price,
        min(current_price)                        as min_price,
        max(current_price)                        as max_price,
        round(avg(pct_change_24h)::numeric, 4)    as avg_pct_change_24h,
        round(avg(volatility_24h)::numeric, 6)    as avg_volatility,
        round(avg(rsi)::numeric, 2)               as avg_rsi,
        round(avg(total_volume)::numeric, 0)      as avg_volume,
        max(market_cap)                           as market_cap
    from prices
    group by coin_id, symbol, name, date
),

daily_sentiment as (
    select
        coin_id,
        date,
        round(avg(avg_sentiment_score)::numeric, 4) as daily_avg_sentiment,
        round(avg(sentiment_index)::numeric, 4)     as daily_sentiment_index,
        sum(post_count)                             as total_readings,
        case
            when avg(avg_sentiment_score) >= 0.6 then 'bullish'
            when avg(avg_sentiment_score) <= 0.4 then 'bearish'
            else 'neutral'
        end                                         as dominant_sentiment
    from sentiment
    group by coin_id, date
)

select
    p.coin_id,
    p.symbol,
    p.name,
    p.date,
    p.avg_price,
    p.min_price,
    p.max_price,
    p.avg_pct_change_24h,
    p.avg_volatility,
    p.avg_rsi,
    p.avg_volume,
    p.market_cap,
    coalesce(s.daily_avg_sentiment, 0.5)      as daily_avg_sentiment,
    coalesce(s.daily_sentiment_index, 0)      as daily_sentiment_index,
    coalesce(s.total_readings, 0)             as reddit_posts,
    coalesce(s.dominant_sentiment, 'neutral') as dominant_sentiment
from daily_prices p
left join daily_sentiment s
    on p.coin_id = s.coin_id
    and p.date   = s.date
