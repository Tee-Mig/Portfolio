from __future__ import annotations

import os
from datetime import datetime, timedelta

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sqlalchemy import create_engine, text
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Crypto Market Pulse",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Palette
BG      = "#070b12"
CARD    = "#0d1b2e"
CHART   = "#0f2040"
BORDER  = "rgba(255,255,255,0.07)"
CYAN    = "#00d4ff"
PURPLE  = "#7c3aed"
YELLOW  = "#f59e0b"
PINK    = "#ec4899"
GREEN   = "#10b981"
RED     = "#ef4444"
MUTED   = "rgba(255,255,255,0.35)"
TEXT    = "rgba(255,255,255,0.88)"

COIN_COLORS  = {"bitcoin": CYAN, "ethereum": PURPLE, "binancecoin": YELLOW, "solana": PINK}
COIN_SYMBOLS = {"bitcoin": "BTC", "ethereum": "ETH", "binancecoin": "BNB", "solana": "SOL"}
COINS_ALL    = ["bitcoin", "ethereum", "binancecoin", "solana"]


def rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
*, *::before, *::after {{ box-sizing: border-box; font-family: 'Inter', sans-serif !important; }}

/* ── Page ── */
.stApp, .main,
[data-testid="stAppViewContainer"],
section[data-testid="stMain"] {{
    background: {BG} !important;
    background-image:
        radial-gradient(ellipse at 20% 5%,  rgba(0,212,255,0.04) 0%, transparent 45%),
        radial-gradient(ellipse at 80% 90%, rgba(124,58,237,0.05) 0%, transparent 45%) !important;
}}
section[data-testid="stSidebar"],
[data-testid="collapsedControl"] {{ display: none !important; }}
[data-testid="stHeader"]         {{ display: none !important; }}
[data-testid="stToolbar"]        {{ display: none !important; }}
.block-container                 {{ padding: 0 2.5rem 3rem !important; max-width: 1500px !important; }}

/* ── Sticky controls bar — full-bleed ── */
div[data-testid="stVerticalBlock"] > div:has([data-testid="stSlider"]) {{
    position: sticky !important;
    top: 0 !important;
    z-index: 999 !important;
    background: rgba(7,11,18,0.94) !important;
    backdrop-filter: blur(18px) !important;
    -webkit-backdrop-filter: blur(18px) !important;
    /* break out of block-container horizontal padding */
    margin-left: -2.5rem !important;
    margin-right: -2.5rem !important;
    padding: 0.6rem 2.5rem 1.0rem !important;
}}

/* ── Tabs — centred, no underline chrome ── */
[data-baseweb="tab-list"] {{
    background: transparent !important;
    border-bottom: 1px solid {BORDER} !important;
    border-radius: 0 !important;
    gap: 0 !important;
    padding: 0 !important;
    justify-content: center !important;
    display: flex !important;
}}
[data-baseweb="tab"] {{
    background: transparent !important;
    border-radius: 0 !important;
    color: {MUTED} !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 0.8rem 2.2rem !important;
    border-bottom: 2px solid transparent !important;
    transition: all .18s !important;
    letter-spacing: 0.02em !important;
}}
[data-baseweb="tab"]:hover       {{ color: {TEXT} !important; }}
[aria-selected="true"] {{
    color: {CYAN} !important;
    border-bottom: 2px solid {CYAN} !important;
    text-shadow: 0 0 16px rgba(0,212,255,.45) !important;
}}
[data-baseweb="tab-highlight"],
[data-baseweb="tab-border"]      {{ display: none !important; }}
[data-baseweb="tab-panel"]       {{ padding: 0 !important; }}

/* ── Inputs ── */
[data-baseweb="select"] > div {{
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    border-radius: 8px !important;
    font-size: 0.8rem !important;
}}
[data-baseweb="tag"] {{
    background: rgba(0,212,255,0.12) !important;
    border: 1px solid rgba(0,212,255,0.25) !important;
    border-radius: 5px !important;
}}
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {{
    background: {CYAN} !important;
    box-shadow: 0 0 0 3px rgba(0,212,255,.25) !important;
}}
/* Hide slider tick bar (the line below the track) */
[data-testid="stSliderTickBarMin"],
[data-testid="stSliderTickBarMax"],
[data-testid="stTickBar"] {{ display: none !important; }}
[data-testid="stSlider"] > div > div:last-child {{
    display: none !important;
}}

/* ── Typography ── */
h1,h2,h3 {{ color:{TEXT} !important; }}
p         {{ color:{MUTED} !important; font-size:.82rem !important; }}
label     {{ color:{MUTED} !important; font-size:.76rem !important; }}
hr        {{ border-color:{BORDER} !important; margin:0 !important; }}

/* ── Alerts ── */
[data-testid="stAlert"] {{ border-radius:12px !important; border:none !important; }}

/* ── DataFrame ── */
[data-testid="stDataFrame"] {{
    border-radius:14px !important; overflow:hidden !important;
    border:1px solid {BORDER} !important;
}}

/* ── Plotly wrapper ── */
div[data-testid="stPlotlyChart"] {{
    clip-path: inset(0% round 16px) !important;
}}
div[data-testid="stPlotlyChart"],
div[data-testid="stPlotlyChart"] > div,
div[data-testid="stPlotlyChart"] .js-plotly-plot,
div[data-testid="stPlotlyChart"] .plot-container,
div[data-testid="stPlotlyChart"] .svg-container {{
    border-radius: 16px !important;
    overflow: hidden !important;
}}
</style>
""", unsafe_allow_html=True)


# DB
@st.cache_resource
def get_engine():
    url = os.getenv("DATABASE_URL", "postgresql://admin:admin@postgres:5432/crypto_pulse")
    return create_engine(url)

@st.cache_data(ttl=300)
def run_query(sql: str) -> pd.DataFrame:
    with get_engine().connect() as conn:
        return pd.read_sql(text(sql), conn)


def stat_card(label: str, value: str, delta: str = "", positive: bool = True,
              rows: list[tuple] = [], accent: str = CYAN) -> str:
    arrow       = "▲" if positive else "▼"
    delta_color = GREEN if positive else RED
    delta_html  = (
        f'<div style="color:{delta_color};font-size:.76rem;font-weight:600;margin-top:5px">'
        f'{arrow} {delta}</div>'
    ) if delta else ""
    rows_html = "".join(
        f'<div style="display:flex;justify-content:space-between;margin-top:7px;'
        f'padding-top:7px;border-top:1px solid rgba(255,255,255,0.04)">'
        f'<span style="color:{MUTED};font-size:.69rem">{k}</span>'
        f'<span style="color:{TEXT};font-size:.69rem;font-weight:600">{v}</span></div>'
        for k, v in rows
    )
    return f"""
<div style="
    background:linear-gradient(160deg,rgba(15,32,64,0.95) 0%,rgba(13,27,46,0.95) 100%);
    border:1px solid {BORDER};
    border-top:2px solid {accent};
    border-radius:16px;
    padding:1.2rem 1.3rem 1.1rem;
    position:relative;overflow:hidden;
">
  <div style="position:absolute;top:0;left:0;right:0;height:50px;
              background:linear-gradient(180deg,{rgba(accent,0.07)},transparent);
              pointer-events:none"></div>
  <div style="color:{MUTED};font-size:.66rem;text-transform:uppercase;
              letter-spacing:.11em;margin-bottom:9px">{label}</div>
  <div style="color:{accent};font-size:1.65rem;font-weight:800;
              letter-spacing:-1px;line-height:1;
              text-shadow:0 0 20px {rgba(accent,0.4)}">{value}</div>
  {delta_html}
  {rows_html}
</div>"""


def section_label(txt: str) -> None:
    st.markdown(
        f'<div style="color:{MUTED};font-size:.65rem;text-transform:uppercase;'
        f'letter-spacing:.13em;font-weight:600;margin:1.5rem 0 .65rem">{txt}</div>',
        unsafe_allow_html=True,
    )


def chart_cfg(title: str = "", h: int = 280) -> dict:
    return dict(
        paper_bgcolor=CHART,
        plot_bgcolor=CHART,
        font=dict(color=MUTED, family="Inter,sans-serif", size=11),
        height=h,
        margin=dict(l=36, r=36, t=52 if title else 40, b=36),
        title=dict(text=title, font=dict(size=11, color=MUTED), x=0.01) if title else {},
        showlegend=False,
    )


def rounded_chart(fig: go.Figure, h: int = 280,
                  legend: list[tuple[str, str]] | None = None) -> None:
    PAD_PX = 12
    RADIUS  = 10
    fig.update_layout(autosize=True, height=h)
    chart_html = fig.to_html(
        full_html=False,
        include_plotlyjs="cdn",
        config={"displayModeBar": False, "responsive": True},
    )
    legend_html = ""
    if legend:
        items = "".join(
            f'<span style="display:inline-flex;align-items:center;gap:5px">'
            f'<span style="width:16px;height:2px;background:{color};'
            f'border-radius:1px;display:inline-block"></span>'
            f'<span style="color:rgba(226,232,240,0.9);font-size:11px;'
            f'font-weight:500;font-family:Inter,sans-serif">{label}</span>'
            f'</span>'
            for label, color in legend
        )
        legend_html = (
            f'<div style="position:absolute;top:{PAD_PX+8}px;right:{PAD_PX+8}px;'
            f'display:inline-flex;align-items:center;gap:12px;'
            f'background:rgba(13,27,46,0.85);border:1px solid rgba(255,255,255,0.08);'
            f'border-radius:8px;padding:5px 12px;z-index:100">{items}</div>'
        )
    resize_script = """<script>
    window.addEventListener('load', function(){
        function rl(){
            var el = document.querySelector('.js-plotly-plot');
            if(el && window.Plotly){ Plotly.relayout(el, {autosize:true}); }
        }
        rl();
        [150, 500, 1200].forEach(function(d){ setTimeout(rl, d); });
        if(window.ResizeObserver){
            var el = document.querySelector('.js-plotly-plot');
            if(el){ new ResizeObserver(rl).observe(el); }
            new ResizeObserver(rl).observe(document.body);
        }
    });
    </script>"""
    components.html(
        f"""<html><head><style>
          html,body{{margin:0;padding:0;background:{BG};overflow:hidden;}}
          .outer{{padding:{PAD_PX}px;box-sizing:border-box;width:100%;position:relative;}}
          .wrap{{border-radius:{RADIUS}px;overflow:hidden;width:100%;}}
        </style></head><body>
        <div class="outer">
          <div class="wrap">{chart_html}</div>
          {legend_html}
        </div>
        {resize_script}
        </body></html>""",
        height=h + PAD_PX * 2 + 2,
        scrolling=False,
    )


AXIS = dict(
    gridcolor="rgba(255,255,255,0.04)",
    zeroline=False,
    linecolor="rgba(0,0,0,0)",
    tickfont=dict(size=9, color=MUTED),
    showgrid=True,
)
XAXIS = {**AXIS, "tickformat": "%d %b", "dtick": "D1"}

PAD = '<div style="padding:0 2.5rem">'
END = '</div>'


# Hero Header
try:
    _last = run_query("select max(date) as d from gold.kpi_daily_summary")
    _val  = _last["d"].iloc[0]
    last_str = pd.to_datetime(_val).strftime("%d %b %Y") if _val is not None else "—"
except Exception:
    last_str = "—"

st.markdown(f"""
<div style="text-align:center;padding:2.5rem 2rem 2.2rem;margin-bottom:1.2rem">
    <div style="color:{CYAN};font-size:.63rem;text-transform:uppercase;
                letter-spacing:.22em;font-weight:600;margin-bottom:8px">
        ● Live Pipeline
    </div>
    <div style="color:#ffffff;font-size:2rem;font-weight:900;
                letter-spacing:-.8px;line-height:1.1;
                text-shadow:0 0 40px rgba(0,212,255,.18)">
        Crypto Market Pulse
    </div>
    <div style="color:{MUTED};font-size:.76rem;margin-top:6px">
        Dernière donnée · {last_str}
    </div>
</div>
""", unsafe_allow_html=True)


# sticky controls
with st.container():
    _, ctrl_a, ctrl_b, _ = st.columns([1.5, 1.8, 2.8, 1.5])
    with ctrl_a:
        days = st.slider("Historique (jours)", 1, 30, 7)
    with ctrl_b:
        coins_selected = st.multiselect(
            "Cryptos",
            COINS_ALL,
            default=["bitcoin", "ethereum"],
            format_func=lambda c: f"{COIN_SYMBOLS[c]} · {c.capitalize()}",
        )

if not coins_selected:
    st.warning("Sélectionne au moins une crypto.")
    st.stop()

coin_filter = "'" + "','".join(coins_selected) + "'"
start_date  = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")



# Tabs
tab1, tab2, tab3 = st.tabs([
    "Vue Marché",
    "Fear & Greed Index",
    "Corrélations",
])


# Tab 1 — Vue Marché
with tab1:
    today_df = run_query(f"""
        select coin_id, symbol, name, avg_price, avg_pct_change_24h,
               avg_volatility, avg_rsi, dominant_sentiment
        from gold.kpi_top_movers
        where date = (select max(date) from gold.kpi_top_movers)
          and coin_id in ({coin_filter})
        order by avg_pct_change_24h desc
    """)
    price_hist = run_query(f"""
        select coin_id, avg_price, avg_volatility, avg_rsi, date
        from gold.kpi_daily_summary
        where date >= '{start_date}'
          and coin_id in ({coin_filter})
        order by date
    """)

    st.markdown(f'{PAD}<div style="display:flex;gap:2rem;margin-top:1.5rem">', unsafe_allow_html=True)
    left, center = st.columns([1, 4.8], gap="large")

    with left:
        section_label("Snapshot du jour")
        if today_df.empty:
            st.info("Aucune donnée. Lance les DAGs Airflow.")
        else:
            cards_html = "".join(
                stat_card(
                    f"{(row['symbol'] or row['coin_id']).upper()} · {row['name']}",
                    f"${row['avg_price']:,.0f}",
                    f"{abs(row['avg_pct_change_24h'] or 0):.2f}%",
                    (row["avg_pct_change_24h"] or 0) >= 0,
                    [("RSI",        f"{row['avg_rsi'] or 0:.0f}"),
                     ("Volatilité", f"{row['avg_volatility'] or 0:.4f}"),
                     ("Sentiment",  row.get("dominant_sentiment") or "—")],
                    COIN_COLORS.get(row["coin_id"], CYAN),
                )
                for _, row in today_df.iterrows()
            )
            st.markdown(
                f'<div style="display:flex;flex-direction:column;'
                f'justify-content:space-between;gap:1.9rem;min-height:304px">'
                f'{cards_html}</div>',
                unsafe_allow_html=True,
            )

    with center:
        if not price_hist.empty:
            section_label(f"Évolution des prix — {days} jours")
            fig_p = go.Figure()
            for coin in coins_selected:
                d     = price_hist[price_hist["coin_id"] == coin]
                color = COIN_COLORS.get(coin, CYAN)
                fig_p.add_trace(go.Scatter(
                    x=d["date"], y=d["avg_price"],
                    name=COIN_SYMBOLS.get(coin, coin),
                    mode="lines",
                    line=dict(color=color, width=2.5, shape="spline", smoothing=1.2),
                    fill="tozeroy",
                    fillcolor=rgba(color, 0.13),
                ))
            fig_p.update_layout(**chart_cfg("Prix moyen journalier (USD)", 290))
            fig_p.update_xaxes(**XAXIS)
            fig_p.update_yaxes(**AXIS)
            rounded_chart(fig_p, h=290,
                          legend=[(COIN_SYMBOLS.get(c, c), COIN_COLORS.get(c, CYAN)) for c in coins_selected])

            c1, c2 = st.columns(2, gap="medium")
            with c1:
                section_label("Volatilité horaire")
                fig_v = go.Figure()
                for coin in coins_selected:
                    d     = price_hist[price_hist["coin_id"] == coin]
                    color = COIN_COLORS.get(coin, CYAN)
                    fig_v.add_trace(go.Scatter(
                        x=d["date"], y=d["avg_volatility"],
                        name=COIN_SYMBOLS.get(coin, coin),
                        line=dict(color=color, width=2, shape="spline", smoothing=1.2),
                        fill="tozeroy", fillcolor=rgba(color, 0.12),
                    ))
                fig_v.update_layout(**chart_cfg(h=210))
                fig_v.update_xaxes(**XAXIS)
                fig_v.update_yaxes(**AXIS)
                rounded_chart(fig_v, h=210,
                              legend=[(COIN_SYMBOLS.get(c, c), COIN_COLORS.get(c, CYAN)) for c in coins_selected])

            with c2:
                section_label("RSI (14 périodes)")
                fig_r = go.Figure()
                for coin in coins_selected:
                    d     = price_hist[price_hist["coin_id"] == coin]
                    color = COIN_COLORS.get(coin, CYAN)
                    fig_r.add_trace(go.Scatter(
                        x=d["date"], y=d["avg_rsi"],
                        name=COIN_SYMBOLS.get(coin, coin),
                        line=dict(color=color, width=2, shape="spline", smoothing=1.2),
                    ))
                fig_r.add_hrect(y0=70, y1=100, fillcolor=rgba(RED,   0.07), line_width=0)
                fig_r.add_hrect(y0=0,  y1=30,  fillcolor=rgba(GREEN, 0.07), line_width=0)
                fig_r.add_hline(y=70, line_dash="dot", line_color=rgba(RED,   0.4), line_width=1)
                fig_r.add_hline(y=30, line_dash="dot", line_color=rgba(GREEN, 0.4), line_width=1)
                fig_r.update_layout(**chart_cfg(h=210))
                fig_r.update_xaxes(**XAXIS)
                fig_r.update_yaxes(**AXIS, range=[0, 100])
                rounded_chart(fig_r, h=210,
                              legend=[(COIN_SYMBOLS.get(c, c), COIN_COLORS.get(c, CYAN)) for c in coins_selected])

    st.markdown(END, unsafe_allow_html=True)


# Tab 2 — Fear & Greed Index
with tab2:
    sent_df = run_query(f"""
        select coin_id, date, daily_avg_sentiment, daily_sentiment_index,
               reddit_posts, dominant_sentiment
        from gold.kpi_daily_summary
        where date >= '{start_date}'
          and coin_id in ({coin_filter})
        order by date
    """)
    price_df = run_query(f"""
        select coin_id, date, avg_price
        from gold.kpi_daily_summary
        where date >= '{start_date}'
          and coin_id in ({coin_filter})
        order by date
    """)

    if sent_df.empty:
        st.markdown(f"{PAD}", unsafe_allow_html=True)
        st.info("Pas encore de données de sentiment. Lance le DAG sentiment_ingestion.")
        st.markdown(END, unsafe_allow_html=True)
    else:
        today_sent = sent_df[sent_df["date"] == sent_df["date"].max()]
        left, center = st.columns([1, 4.8], gap="large")

        with left:
            section_label("Score du jour")
            cards_html = "".join(
                stat_card(
                    COIN_SYMBOLS.get(row["coin_id"], row["coin_id"]),
                    f"{float(row['daily_avg_sentiment']) * 100:.0f} / 100",
                    "Avidité" if float(row["daily_avg_sentiment"]) * 100 >= 60
                    else ("Peur" if float(row["daily_avg_sentiment"]) * 100 <= 40 else "Neutre"),
                    float(row["daily_avg_sentiment"]) * 100 >= 50,
                    [("Statut",       "Avidité" if float(row["daily_avg_sentiment"]) * 100 >= 60
                                      else ("Peur" if float(row["daily_avg_sentiment"]) * 100 <= 40 else "Neutre")),
                     ("Index [-1,1]", f"{float(row.get('daily_sentiment_index') or 0):.2f}"),
                     ("Lectures",     str(int(row.get("reddit_posts") or 0)))],
                    COIN_COLORS.get(row["coin_id"], CYAN),
                )
                for _, row in today_sent.iterrows()
            )
            st.markdown(
                f'<div style="display:flex;flex-direction:column;'
                f'justify-content:space-between;gap:1.9rem;min-height:275px">'
                f'{cards_html}</div>',
                unsafe_allow_html=True,
            )

        with center:
            section_label("Jauges Fear & Greed")
            gcols = st.columns(len(today_sent), gap="medium")
            for i, (_, row) in enumerate(today_sent.iterrows()):
                val   = float(row["daily_avg_sentiment"]) * 100
                sym   = COIN_SYMBOLS.get(row["coin_id"], row["coin_id"])
                mood  = "Avidité" if val >= 60 else ("Peur" if val <= 40 else "Neutre")
                bar_c = GREEN if val >= 60 else (RED if val <= 40 else YELLOW)

                g = go.Figure(go.Indicator(
                    mode="gauge",
                    value=val,
                    title=dict(
                        text=f"<b style='color:white'>{sym}</b><br>"
                             f"<span style='font-size:.75em;color:{MUTED}'>{mood}</span>",
                        font=dict(size=13),
                    ),
                    domain=dict(x=[0, 1], y=[0.18, 1]),
                    gauge=dict(
                        axis=dict(range=[0, 100], nticks=6,
                                  tickfont=dict(size=9, color=MUTED),
                                  tickcolor=BORDER),
                        bar=dict(color=bar_c, thickness=0.18),
                        bgcolor=CHART,
                        borderwidth=0,
                        steps=[
                            dict(range=[0,  25],  color=rgba(RED,    0.09)),
                            dict(range=[25, 45],  color=rgba(RED,    0.03)),
                            dict(range=[45, 55],  color=rgba(YELLOW, 0.03)),
                            dict(range=[55, 75],  color=rgba(GREEN,  0.03)),
                            dict(range=[75, 100], color=rgba(GREEN,  0.09)),
                        ],
                        threshold=dict(
                            line=dict(color="rgba(255,255,255,0.25)", width=2),
                            thickness=0.7, value=50,
                        ),
                    ),
                ))
                g.add_annotation(
                    x=0.5, y=0.08, xref="paper", yref="paper",
                    text=f"<b>{val:.0f}</b>",
                    showarrow=False,
                    font=dict(size=28, color=bar_c, family="Inter,sans-serif"),
                )
                g.update_layout(
                    height=210, margin=dict(t=60, b=20, l=24, r=24),
                    paper_bgcolor=CHART,
                    plot_bgcolor=CHART,
                    font=dict(family="Inter,sans-serif"),
                )
                with gcols[i]:
                    rounded_chart(g, h=210)

            section_label("Sentiment vs Prix")
            for coin in coins_selected:
                s     = sent_df[sent_df["coin_id"] == coin]
                p     = price_df[price_df["coin_id"] == coin]
                if s.empty or p.empty:
                    continue
                color = COIN_COLORS.get(coin, CYAN)
                sym   = COIN_SYMBOLS.get(coin, coin)
                fig   = make_subplots(specs=[[{"secondary_y": True}]])
                fig.add_trace(go.Bar(
                    x=s["date"], y=s["daily_avg_sentiment"] * 100,
                    name="Fear & Greed",
                    marker=dict(color=color, opacity=0.4, line=dict(width=0)),
                ), secondary_y=False)
                fig.add_trace(go.Scatter(
                    x=p["date"], y=p["avg_price"],
                    name="Prix (USD)",
                    line=dict(color="#ffffff", width=2, shape="spline", smoothing=1.2),
                    fill="tozeroy", fillcolor="rgba(255,255,255,0.06)",
                ), secondary_y=True)
                fig.update_layout(**chart_cfg(sym, 230))
                fig.update_xaxes(**XAXIS)
                fig.update_yaxes(**AXIS, range=[0, 110], secondary_y=False)
                fig.update_yaxes(**AXIS, secondary_y=True)
                rounded_chart(fig, h=230,
                              legend=[("Fear & Greed", color), ("Prix (USD)", "#ffffff")])


# tab 3 — Corrélation
with tab3:
    corr_df = run_query(f"""
        select coin_id, symbol, date,
               sentiment_prev_day, avg_pct_change_24h,
               sentiment_price_corr_7d,
               correlation_strength, correlation_direction
        from gold.kpi_correlation
        where date >= '{start_date}'
          and coin_id in ({coin_filter})
        order by date
    """)

    if corr_df.empty:
        st.markdown(f"{PAD}", unsafe_allow_html=True)
        st.info("Pas encore assez de données (minimum 2 jours de pipeline requis).")
        st.markdown(END, unsafe_allow_html=True)
    else:
        latest = corr_df[corr_df["date"] == corr_df["date"].max()].drop_duplicates("coin_id")
        left, center = st.columns([1, 4.8], gap="large")

        with left:
            section_label("Corrélation 7 jours")
            cards_html = "".join(
                stat_card(
                    COIN_SYMBOLS.get(row["coin_id"], row["coin_id"]),
                    "N/A" if pd.isna(row["sentiment_price_corr_7d"])
                          else f"r = {row['sentiment_price_corr_7d']:.2f}",
                    "" if pd.isna(row["sentiment_price_corr_7d"])
                       else row["correlation_strength"],
                    row.get("correlation_direction") == "positive",
                    [("Données", "insuffisantes")] if pd.isna(row["sentiment_price_corr_7d"])
                    else [("Force",     row["correlation_strength"]),
                          ("Direction", row["correlation_direction"])],
                    COIN_COLORS.get(row["coin_id"], CYAN),
                )
                for _, row in latest.iterrows()
            )
            st.markdown(
                f'<div style="display:flex;flex-direction:column;'
                f'justify-content:space-between;gap:1.9rem;min-height:270px">'
                f'{cards_html}</div>',
                unsafe_allow_html=True,
            )

        with center:
            section_label("Corrélation glissante 7 jours (r de Pearson)")
            fig_c = go.Figure()
            for coin in coins_selected:
                d     = corr_df[corr_df["coin_id"] == coin]
                color = COIN_COLORS.get(coin, CYAN)
                fig_c.add_trace(go.Scatter(
                    x=d["date"], y=d["sentiment_price_corr_7d"],
                    name=COIN_SYMBOLS.get(coin, coin),
                    line=dict(color=color, width=2.5, shape="spline", smoothing=1.2),
                    fill="tozeroy", fillcolor=rgba(color, 0.12),
                ))
            fig_c.add_hline(y=0,    line_dash="dot", line_color="rgba(255,255,255,0.2)", line_width=1)
            fig_c.add_hline(y=0.4,  line_dash="dot", line_color=rgba(GREEN, 0.4), line_width=1)
            fig_c.add_hline(y=-0.4, line_dash="dot", line_color=rgba(RED,   0.4), line_width=1)
            fig_c.add_hrect(y0=0.4,  y1=1,  fillcolor=rgba(GREEN, 0.05), line_width=0)
            fig_c.add_hrect(y0=-1, y1=-0.4, fillcolor=rgba(RED,   0.05), line_width=0)
            fig_c.update_layout(**chart_cfg(h=270))
            fig_c.update_xaxes(**XAXIS)
            fig_c.update_yaxes(**AXIS, range=[-1, 1])
            rounded_chart(fig_c, h=270,
                          legend=[(COIN_SYMBOLS.get(c, c), COIN_COLORS.get(c, CYAN)) for c in coins_selected])

            section_label("Scatter : Sentiment J-1 vs Variation prix J")
            fig_s = go.Figure()
            for coin in coins_selected:
                d     = corr_df[corr_df["coin_id"] == coin]
                color = COIN_COLORS.get(coin, CYAN)
                fig_s.add_trace(go.Scatter(
                    x=d["sentiment_prev_day"],
                    y=d["avg_pct_change_24h"],
                    name=COIN_SYMBOLS.get(coin, coin),
                    mode="markers",
                    marker=dict(color=color, size=9, opacity=0.8,
                                line=dict(color=rgba(color, 0.4), width=1)),
                ))
            fig_s.update_layout(**chart_cfg(h=230))
            fig_s.update_xaxes(**AXIS, title=dict(text="Fear & Greed Score (J-1)",
                                                   font=dict(size=10, color=MUTED)))
            fig_s.update_yaxes(**AXIS, title=dict(text="Variation prix 24h % (J)",
                                                   font=dict(size=10, color=MUTED)))
            rounded_chart(fig_s, h=230,
                          legend=[(COIN_SYMBOLS.get(c, c), COIN_COLORS.get(c, CYAN)) for c in coins_selected])

            section_label("Tableau récapitulatif")
            tbl = latest[["coin_id","sentiment_price_corr_7d",
                          "correlation_strength","correlation_direction"]].rename(columns={
                "coin_id": "Crypto", "sentiment_price_corr_7d": "r (7 jours)",
                "correlation_strength": "Force", "correlation_direction": "Direction",
            })
            st.dataframe(tbl, use_container_width=True, hide_index=True)

# bottom padding
st.markdown('<div style="height:3rem"></div>', unsafe_allow_html=True)
