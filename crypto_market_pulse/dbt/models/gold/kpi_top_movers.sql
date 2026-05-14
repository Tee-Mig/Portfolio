{{ config(materialized='table', schema='gold') }}

with daily as (
    select * from {{ ref('kpi_daily_summary') }}
),

ranked as (
    select
        *,
        rank() over (partition by date order by avg_pct_change_24h desc) as rank_gainers,
        rank() over (partition by date order by avg_pct_change_24h asc)  as rank_losers,
        rank() over (partition by date order by reddit_posts desc)        as rank_buzz
    from daily
)

select
    coin_id,
    symbol,
    name,
    date,
    avg_price,
    avg_pct_change_24h,
    avg_volatility,
    avg_rsi,
    daily_avg_sentiment,
    dominant_sentiment,
    reddit_posts,
    rank_gainers,
    rank_losers,
    rank_buzz,
    case
        when rank_gainers <= 3 then 'top_gainer'
        when rank_losers  <= 3 then 'top_loser'
        else 'neutral'
    end as mover_category
from ranked
