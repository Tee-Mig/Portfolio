{{ config(materialized='table', schema='gold') }}

with daily as (
    select * from {{ ref('kpi_daily_summary') }}
),

-- Lag sentiment by 1 day to test whether yesterday's sentiment predicts today's price move
lagged as (
    select
        coin_id,
        symbol,
        date,
        daily_avg_sentiment,
        daily_sentiment_index,
        avg_pct_change_24h,
        reddit_posts,
        lag(daily_avg_sentiment, 1)   over (partition by coin_id order by date) as sentiment_prev_day,
        lag(daily_sentiment_index, 1) over (partition by coin_id order by date) as sentiment_index_prev_day,
        lag(reddit_posts, 1)          over (partition by coin_id order by date) as posts_prev_day
    from daily
),

-- Rolling 7-day Pearson correlation between lagged sentiment and price change
corr_calc as (
    select
        coin_id,
        symbol,
        date,
        sentiment_prev_day,
        avg_pct_change_24h,
        reddit_posts,
        round(
            corr(sentiment_prev_day, avg_pct_change_24h) over (
                partition by coin_id
                order by date
                rows between 6 preceding and current row
            )::numeric, 4
        ) as sentiment_price_corr_7d
    from lagged
    where sentiment_prev_day is not null
)

select
    coin_id,
    symbol,
    date,
    sentiment_prev_day,
    avg_pct_change_24h,
    reddit_posts,
    sentiment_price_corr_7d,
    case
        when abs(sentiment_price_corr_7d) >= 0.7 then 'strong'
        when abs(sentiment_price_corr_7d) >= 0.4 then 'moderate'
        when abs(sentiment_price_corr_7d) >= 0.2 then 'weak'
        else 'none'
    end as correlation_strength,
    case
        when sentiment_price_corr_7d > 0 then 'positive'
        when sentiment_price_corr_7d < 0 then 'negative'
        else 'neutral'
    end as correlation_direction
from corr_calc
