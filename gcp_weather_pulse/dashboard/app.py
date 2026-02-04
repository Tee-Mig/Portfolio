import os
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
from google.cloud import bigquery

# -------------------- Page / thème --------------------
st.set_page_config(page_title="Weather Pulse", page_icon="⛅", layout="wide")

st.markdown("""
<style>
.block-container {max-width: 1320px; padding-top: .5rem;}
#MainMenu, header, footer {visibility: hidden;}

/* palette */
:root { --bg:#0f2033; --panel:#132a44; --panel-2:#12304f; --panel-3:#0d2238;
        --text:#e5eef7; --muted:#9fb3c8; --accent:#38bdf8; --grid:#4c6b8a; }
html, body, [data-testid="stAppViewContainer"] {background: var(--bg); color: var(--text);}
[data-testid="stSidebar"] {background:#0d1a2a; border-right:1px solid var(--panel-3);}
[data-testid="stSidebar"] * {color: var(--text) !important;}
[data-testid="stSidebar"] [data-testid="stImage"] {display:none !important;}

/* Titre sidebar & page */
.side-title { font-weight:800; font-size:1.6rem; letter-spacing:.2px; margin:6px 0 2px 0; color:var(--text); }
.side-sub   { color:var(--muted); font-size:.9rem; margin:0 0 10px 0; }

.page-title { display:flex; align-items:center; justify-content:center; gap:.6rem; margin:.1rem 0 .9rem 0; text-align:center;}
.page-title h1 { margin:0; font-size:2.5rem; font-weight:800; letter-spacing:.2px; color:var(--text); }
.page-title .badge {background:var(--panel-3); color:var(--muted); padding:2px 8px; border-radius:999px; font-size:.85rem; border:1px solid #15314d;}

/* Titres de sections (centrés) */
.section-title {display:flex; justify-content:center; margin:.15rem 0 .55rem 0;}
.section-title h3 {margin:0; font-weight:800; font-size:1.08rem; letter-spacing:.2px; color:var(--text);}

/* KPI cards */
.kpi{ background:var(--panel); border:1px solid var(--panel-3); border-radius:12px;
      padding:12px 14px; box-shadow:0 2px 6px rgba(7,18,30,.35); margin-bottom:12px; }
.kpi .lbl{font-size:.84rem; color:var(--muted); margin-bottom:6px;}
.kpi .val{font-size:1.28rem; font-weight:800; color:var(--text); line-height:1.2;}
.kpi .sub{font-size:.78rem; color:var(--muted); margin-top:4px}

/* Panels */
.panel{ background:var(--panel); border:1px solid var(--panel-3); border-radius:16px;
        padding:14px 16px; box-shadow:0 2px 6px rgba(7,18,30,.35); }

/* Inputs */
.stMultiSelect [data-baseweb="tag"]{background:var(--panel-2)!important; color:var(--text)!important; border-radius:999px!important;}
.stSlider > div > div > div {color:var(--text)!important;}

/* Dataframes */
.stDataFrame, .stDataEditor { background:var(--panel); border:1px solid var(--panel-3); border-radius:12px; padding:6px 6px; }

/* Layout */
div[data-testid="stHorizontalBlock"]{gap:1.1rem !important;}

/* CENTRAGE des charts & tables dans leur colonne (HD) */
div[data-testid="stChart"],
div[data-testid="stVegaLiteChart"],
div[data-testid="stArrowVegaLiteChart"],
div[data-testid="stDataFrame"],
div[data-testid="stDataEditor"] {
  margin-left: auto !important;
  margin-right: auto !important;
}

/* Mobile: stack + KPIs centrés */
@media (max-width:1100px){
  div[data-testid="stHorizontalBlock"]{ flex-direction:column !important; gap:1rem !important; }
  div[data-testid="column"]{width:100% !important; flex:1 1 100% !important;}
  .kpi{padding:10px 12px; margin:0 auto 14px auto; max-width:520px; text-align:center;}
  .kpi .lbl{font-size:.8rem} .kpi .val{font-size:1.16rem} .kpi .sub{font-size:.75rem}
}

/* Boutons Télécharger centrés (global) */
div[data-testid="stDownloadButton"] { display:flex !important; justify-content:center !important; }
div[data-testid="stDownloadButton"] > button { min-width:220px; font-weight:700; text-align:center; }
</style>
""", unsafe_allow_html=True)

# -------------------- Helpers --------------------
PROJECT = os.environ.get("GCP_PROJECT") or st.secrets.get("GCP_PROJECT")

def unique_cols(cols: list[str]) -> list[str]:
    seen = set()
    out = []
    for c in cols:
        if c not in seen:
            out.append(c)
            seen.add(c)
    return out

def bq_client() -> bigquery.Client:
    if not PROJECT:
        st.error("GCP_PROJECT manquant (variable d'environnement ou st.secrets).")
        st.stop()
    return bigquery.Client(project=PROJECT)

def query_df(sql: str, job_config: bigquery.QueryJobConfig | None = None) -> pd.DataFrame:
    return bq_client().query(sql, job_config=job_config).to_dataframe(create_bqstorage_client=True)

def to_paris(ts) -> pd.Timestamp:
    ts = pd.to_datetime(ts, utc=True)
    return ts.tz_convert("Europe/Paris")

def section_title(text: str):
    st.markdown(f'<div class="section-title"><h3>{text}</h3></div>', unsafe_allow_html=True)

@st.cache_data(show_spinner=False, ttl=3600)
def available_cols_for_view(project: str, schema: str, view_name: str) -> set[str]:
    try:
        sql = f"""
        SELECT column_name
        FROM `{project}.{schema}.INFORMATION_SCHEMA.COLUMNS`
        WHERE table_name = '{view_name}'
        """
        df = query_df(sql)
        return set(df["column_name"].astype(str).tolist()) if not df.empty else set()
    except Exception:
        return set()

def compute_feels_like_c(temp_c: pd.Series, rh: pd.Series, wind_ms: pd.Series) -> pd.Series:
    t = pd.to_numeric(temp_c, errors="coerce").to_numpy(dtype=float)
    h = pd.to_numeric(rh, errors="coerce").to_numpy(dtype=float)
    wms = pd.to_numeric(wind_ms, errors="coerce").to_numpy(dtype=float)
    w = wms * 3.6  # km/h

    out = np.full_like(t, np.nan, dtype=float)

    cold = t <= 10
    out[cold] = 13.12 + 0.6215 * t[cold] - 11.37 * (w[cold] ** 0.16) + 0.3965 * t[cold] * (w[cold] ** 0.16)

    hot = t >= 27
    e = (h / 100.0) * 6.105 * np.exp((17.27 * t) / (237.7 + t))
    out[hot] = t[hot] + 0.33 * e[hot] - 0.70 * wms[hot] - 4.0

    mid = ~(cold | hot)
    out[mid] = t[mid]

    return pd.Series(out, index=temp_c.index, dtype="float64")

# -------------------- Titre global --------------------
st.markdown("""
<div class="page-title">
  <h1>Weather Pulse</h1><span class="badge">Live Analytics</span>
</div>
""", unsafe_allow_html=True)

# -------------------- Sidebar (filtres) --------------------
with st.sidebar:
    st.markdown('<div class="side-title">Weather Pulse</div>', unsafe_allow_html=True)
    st.markdown('<div class="side-sub">Tableau de bord</div>', unsafe_allow_html=True)

    st.markdown("### Filtres")
    default_cities = ["Paris", "Marseille", "Bordeaux"]

    cities_df_list = query_df(f"SELECT DISTINCT city FROM `{PROJECT}.weather.v_hourly_city` ORDER BY city")
    all_cities = cities_df_list["city"].tolist() if not cities_df_list.empty else default_cities
    if not set(default_cities).issubset(set(all_cities)):
        default_cities = all_cities[:3] if all_cities else []

    sel_cities = st.multiselect("Villes", options=all_cities, default=default_cities, key="cities")
    hours_back = st.slider("Fenêtre horaire (heures)", min_value=6, max_value=168, value=24, step=6, key="hours_back")
    days_back  = st.slider("Période (jours)", min_value=3, max_value=14, value=7, step=1, key="days_back")

# -------------------- KPIs --------------------
last_ts_df = query_df(f"SELECT MAX(ts) AS last_ts FROM `{PROJECT}.weather.v_hourly_city`")
raw_last = pd.to_datetime(last_ts_df["last_ts"].iloc[0]) if not last_ts_df.empty else None
now_utc  = datetime.now(timezone.utc)
anchor_utc = min(pd.to_datetime(raw_last, utc=True), pd.to_datetime(now_utc, utc=True)) if raw_last is not None else now_utc

last_paris = to_paris(anchor_utc) if raw_last is not None else None
now_paris  = pd.Timestamp.now(tz="Europe/Paris")

if last_paris is None:
    last_val = "—"; age_txt = "—"
else:
    last_val = last_paris.strftime("%d/%m/%Y %H:%M")
    delta = now_paris - last_paris
    mins = int(abs(delta.total_seconds()) // 60)
    age_txt = (f"il y a {mins} min" if mins < 60 else f"il y a {mins//60} h {mins%60} min") if delta.total_seconds() >= 0 \
              else (f"dans {mins} min" if mins < 60 else f"dans {mins//60} h {mins%60} min")

total_rows = None
try:
    meta_df = query_df("""
      SELECT row_count
      FROM `region-eu`.INFORMATION_SCHEMA.TABLES
      WHERE table_schema = 'weather' AND table_name = 'observations'
    """)
    if not meta_df.empty and pd.notna(meta_df.iloc[0]["row_count"]):
        total_rows = int(meta_df.iloc[0]["row_count"])
except Exception:
    total_rows = None

if total_rows is None:
    tr_df = query_df(f"SELECT COUNT(1) AS n FROM `{PROJECT}.weather.observations`")
    total_rows = int(tr_df["n"].iloc[0]) if not tr_df.empty else 0

cities_df_all = query_df(f"SELECT COUNT(DISTINCT city) AS n FROM `{PROJECT}.weather.v_hourly_city`")
n_cities = int(cities_df_all["n"].iloc[0]) if not cities_df_all.empty else 0

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""<div class="kpi"><div class="lbl">Dernier relevé</div>
    <div class="val">{last_val}</div><div class="sub">{age_txt} • Europe/Paris</div></div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class="kpi"><div class="lbl">Total insertions</div>
    <div class="val">{total_rows:,}</div><div class="sub">Depuis le début</div></div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""<div class="kpi"><div class="lbl">Villes</div>
    <div class="val">{n_cities}</div><div class="sub">Couverture</div></div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""<div class="kpi"><div class="lbl">Fenêtre</div>
    <div class="val">{hours_back} h</div><div class="sub">Courbe horaire</div></div>""", unsafe_allow_html=True)

st.markdown("")

# -------------------- Évolution horaire — Température --------------------
def get_anchor_for_selection(project: str, cities: list[str]) -> datetime:
    use_filter = bool(cities)
    sql = f"""
    SELECT MAX(ts) AS last_ts
    FROM `{project}.weather.v_hourly_city`
    WHERE ts <= CURRENT_TIMESTAMP()
      AND (@use_filter = FALSE OR city IN UNNEST(@cities))
    """
    job_cfg = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("use_filter", "BOOL", use_filter),
            bigquery.ArrayQueryParameter("cities", "STRING", cities if use_filter else []),
        ]
    )
    df = query_df(sql, job_cfg)
    if df.empty or pd.isna(df.iloc[0]["last_ts"]):
        return datetime.now(timezone.utc)
    return min(pd.to_datetime(df.iloc[0]["last_ts"], utc=True), datetime.now(timezone.utc))

anchor_sel_utc = get_anchor_for_selection(PROJECT, sel_cities or [])
t_to = anchor_sel_utc
t_from = t_to - timedelta(hours=hours_back)

use_filter = bool(sel_cities)
cities_param = sel_cities if use_filter else []

cols = available_cols_for_view(PROJECT, "weather", "v_hourly_city")
optional = [c for c in [
    "relative_humidity_2m", "precipitation", "wind_speed_10m", "wind_direction_10m", "cloud_cover", "pressure_msl"
] if c in cols]

select_cols = ["city", "ts", "temperature_2m"] + optional
select_sql = ", ".join(select_cols)

hourly_sql = f"""
SELECT {select_sql}
FROM `{PROJECT}.weather.v_hourly_city`
WHERE ts BETWEEN @t_from AND @t_to
  AND (@use_filter = FALSE OR city IN UNNEST(@cities))
ORDER BY ts
"""
hourly_cfg = bigquery.QueryJobConfig(
    use_query_cache=False,
    query_parameters=[
        bigquery.ScalarQueryParameter("t_from", "TIMESTAMP", t_from),
        bigquery.ScalarQueryParameter("t_to",   "TIMESTAMP", t_to),
        bigquery.ScalarQueryParameter("use_filter", "BOOL", use_filter),
        bigquery.ArrayQueryParameter("cities", "STRING", cities_param),
    ]
)
hourly_df = query_df(hourly_sql, hourly_cfg)

left, right = st.columns(2)

with left:
    section_title("Évolution horaire — Température")
    if hourly_df.empty:
        st.markdown('<div class="panel">Aucune donnée pour cette période.</div>', unsafe_allow_html=True)
    else:
        df = hourly_df.copy()
        df["ts"] = pd.to_datetime(df["ts"], utc=True, errors="coerce")
        df["temperature_2m"] = pd.to_numeric(df["temperature_2m"], errors="coerce")
        df = df.dropna(subset=["ts", "temperature_2m"])
        df["ts_paris"] = df["ts"].dt.tz_convert("Europe/Paris").dt.tz_localize(None)

        pivot = (
            df.pivot_table(index="ts_paris", columns="city", values="temperature_2m", aggfunc="mean")
              .sort_index()
              .dropna(how="all")
        )

        if pivot.empty:
            st.markdown('<div class="panel">Aucune donnée à afficher.</div>', unsafe_allow_html=True)
        else:
            t_to_paris = pivot.index.max()
            t_from_paris = t_to_paris - pd.Timedelta(hours=hours_back)
            pivot_win = pivot.loc[(pivot.index >= t_from_paris) & (pivot.index <= t_to_paris)].dropna(how="all")

            if pivot_win.empty:
                st.markdown('<div class="panel">Fenêtre trop petite : aucun point.</div>', unsafe_allow_html=True)
            else:
                if hours_back <= 24:
                    freq = None
                elif hours_back <= 72:
                    freq = "2H"
                else:
                    freq = "3H"

                pivot_plot = pivot_win.resample(freq).mean().dropna(how="all") if freq else pivot_win

                plot_df = pivot_plot.reset_index().rename(columns={"ts_paris": "Date/Heure"})
                span = plot_df["Date/Heure"].max() - plot_df["Date/Heure"].min()
                x_format = "%H:%M" if span <= pd.Timedelta("24H") else "%d/%m %H:%M"

                long_df = plot_df.melt(
                    id_vars=["Date/Heure"],
                    var_name="Ville",
                    value_name="Température (°C)"
                ).dropna(subset=["Température (°C)"])

                chart = (
                    alt.Chart(long_df)
                    .mark_line(strokeWidth=2.5)
                    .encode(
                        x=alt.X("Date/Heure:T", title="Temps (Paris)",
                                axis=alt.Axis(format=x_format, tickCount=8, labelOverlap=True)),
                        y=alt.Y("Température (°C):Q", title="Température (°C)"),
                        color=alt.Color("Ville:N", legend=alt.Legend(title="Villes")),
                        tooltip=[
                            alt.Tooltip("Ville:N"),
                            alt.Tooltip("Date/Heure:T", format="%d/%m/%Y %H:%M"),
                            alt.Tooltip("Température (°C):Q", format=".1f"),
                        ],
                    )
                    .properties(height=420, background="#0f2033")
                    .configure_view(stroke=None)
                    .configure_axis(
                        grid=True, gridColor="#4c6b8a", gridOpacity=0.35,
                        domainColor="#4c6b8a", tickColor="#4c6b8a",
                        labelColor="#e5eef7", titleColor="#e5eef7",
                        titleFontSize=13, labelFontSize=11
                    )
                    .configure_legend(labelColor="#e5eef7", titleColor="#e5eef7")
                )
                st.altair_chart(chart, use_container_width=True)

with right:
    section_title("Voir les données — Horaire")
    if hourly_df.empty:
        st.markdown('<div class="panel">—</div>', unsafe_allow_html=True)
    else:
        table = hourly_df.copy()

        table["_utc_ts"] = pd.to_datetime(table["ts"], utc=True, errors="coerce")
        table = table.dropna(subset=["_utc_ts"])

        table["Date/Heure"] = table["_utc_ts"].dt.tz_convert("Europe/Paris").dt.tz_localize(None)

        table = table.rename(columns={"city": "Ville", "temperature_2m": "Temp (°C)"})
        table["Temp (°C)"] = pd.to_numeric(table["Temp (°C)"], errors="coerce")

        if "relative_humidity_2m" in table.columns:
            table = table.rename(columns={"relative_humidity_2m": "Humidité (%)"})
            table["Humidité (%)"] = pd.to_numeric(table["Humidité (%)"], errors="coerce")

        if "precipitation" in table.columns:
            table = table.rename(columns={"precipitation": "Pluie (mm)"})
            table["Pluie (mm)"] = pd.to_numeric(table["Pluie (mm)"], errors="coerce")

        if "wind_speed_10m" in table.columns:
            table = table.rename(columns={"wind_speed_10m": "Vent (m/s)"})
            table["Vent (m/s)"] = pd.to_numeric(table["Vent (m/s)"], errors="coerce")
            table["Vent (km/h)"] = table["Vent (m/s)"] * 3.6

        table = table.sort_values(["Ville", "_utc_ts"]).reset_index(drop=True)
        table["Δ Temp (°C)"] = table.groupby("Ville")["Temp (°C)"].diff()

        if ("Humidité (%)" in table.columns) and ("Vent (m/s)" in table.columns):
            table["Ressentie (°C)"] = compute_feels_like_c(table["Temp (°C)"], table["Humidité (%)"], table["Vent (m/s)"])

        table = table.sort_values("_utc_ts", ascending=False)

        base_cols = ["Ville", "Date/Heure", "Temp (°C)"]
        extra_cols = [c for c in [
            "Ressentie (°C)", "Temp (°C)",
            "Humidité (%)", "Pluie (mm)", "Vent (m/s)", "Vent (km/h)"
        ] if c in table.columns]

        final_cols = unique_cols(base_cols + extra_cols)

        final_cols = [c for c in final_cols if c in table.columns]

        sort_col = None
        for candidate in ["Date/Heure (UTC)", "UTC", "Date/Heure (Paris)", "Paris"]:
            if candidate in table.columns:
                sort_col = candidate
                break

        view = table[final_cols]
        if sort_col:
            view = view.sort_values(sort_col, ascending=False)

        st.dataframe(view, use_container_width=True, hide_index=True, height=420)
        st.download_button(
            "Télécharger (CSV)",
            data=view.to_csv(index=False).encode("utf-8"),
            file_name="weather_hourly.csv",
            mime="text/csv",
            key="dl_hourly"
        )

# -------------------- Tendances journalières — Température moyenne (Altair axes sur le graphe) --------------------
d_to = to_paris(anchor_utc).date() if raw_last is not None else datetime.now(timezone.utc).date()
d_from = d_to - timedelta(days=days_back - 1)

daily_sql = f"""
SELECT day, avg_temp
FROM `{PROJECT}.weather.v_daily_city`
WHERE day BETWEEN @d_from AND @d_to
ORDER BY day
"""
daily_cfg = bigquery.QueryJobConfig(
    use_query_cache=False,
    query_parameters=[
        bigquery.ScalarQueryParameter("d_from", "DATE", d_from),
        bigquery.ScalarQueryParameter("d_to", "DATE", d_to),
    ]
)
daily_df = query_df(daily_sql, daily_cfg)

b1, b2 = st.columns(2)

with b1:
    section_title("Tendances journalières — Température moyenne")
    if daily_df.empty:
        st.markdown('<div class="panel">Aucune donnée sur la période.</div>', unsafe_allow_html=True)
    else:
        tmp = daily_df.copy()

        tmp["_day"] = pd.to_datetime(tmp["day"], errors="coerce")
        tmp["_avg"] = pd.to_numeric(tmp["avg_temp"], errors="coerce")
        tmp = tmp.dropna(subset=["_day", "_avg"]).sort_values("_day")

        if tmp.empty:
            st.markdown('<div class="panel">Aucune donnée exploitable.</div>', unsafe_allow_html=True)
        else:
            by_day = tmp.groupby("_day", as_index=False)["_avg"].mean()
            by_day = by_day.rename(columns={"_day": "Jour", "_avg": "Température moyenne (°C)"})

            chart_daily = (
                alt.Chart(by_day)
                .mark_bar()
                .encode(
                    x=alt.X(
                        "Jour:T",
                        title="Jour",
                        axis=alt.Axis(
                            format="%d/%m",
                            tickCount=min(days_back, 8),
                            labelAngle=0,
                            labelOverlap=True
                        )
                    ),
                    y=alt.Y("Température moyenne (°C):Q", title="Température moyenne (°C)"),
                    tooltip=[
                        alt.Tooltip("Jour:T", title="Jour", format="%d/%m/%Y"),
                        alt.Tooltip("Température moyenne (°C):Q", format=".1f"),
                    ],
                )
                .properties(height=420, background="#0f2033")
                .configure_view(stroke=None)
                .configure_axis(
                    grid=True, gridColor="#4c6b8a", gridOpacity=0.35,
                    domainColor="#4c6b8a", tickColor="#4c6b8a",
                    labelColor="#e5eef7", titleColor="#e5eef7",
                    titleFontSize=13, labelFontSize=11
                )
            )

            st.altair_chart(chart_daily, use_container_width=True)

with b2:
    section_title("Tableau — Bilan par jour")
    if daily_df.empty:
        st.markdown('<div class="panel">—</div>', unsafe_allow_html=True)
    else:
        tbl = daily_df.copy()
        tbl["_day"] = pd.to_datetime(tbl["day"], errors="coerce")
        tbl["_avg"] = pd.to_numeric(tbl["avg_temp"], errors="coerce")
        tbl = tbl.dropna(subset=["_day", "_avg"]).sort_values("_day")

        tbl = tbl.rename(columns={"day": "Jour", "avg_temp": "Temp. moy (°C)"})
        st.dataframe(tbl[["Jour", "Temp. moy (°C)"]], use_container_width=True, hide_index=True, height=420)

        st.download_button(
            "Télécharger (CSV)",
            data=tbl[["Jour", "Temp. moy (°C)"]].to_csv(index=False).encode("utf-8"),
            file_name="weather_daily.csv",
            mime="text/csv",
            key="dl_daily"
        )
