import pandas as pd
import streamlit as st
from google.cloud import bigquery

# --- Config Streamlit ---
st.set_page_config(page_title="Weather Pulse – France", layout="wide")
st.title("🌦️ Weather Pulse – France")

# --- Client BigQuery (utilise les identifiants par défaut GCP) ---
bq = bigquery.Client()
PROJECT = bq.project  # utile pour f-string

# --- Filtres (sidebar) ---
with st.sidebar:
    st.header("Filtres")
    city = st.selectbox("Ville", ["Paris", "Lyon", "Marseille", "Lille", "Bordeaux"], index=0)
    days = st.slider("Période (jours)", min_value=1, max_value=14, value=7)
    st.caption("Source : vue Gold `weather.v_hourly_city`.")

# --- Requête paramétrée (derniers N jours) ---
sql = f"""
SELECT
  ts,
  temperature_2m,
  relative_humidity_2m,
  precipitation,
  wind_speed_10m
FROM `{PROJECT}.weather.v_hourly_city`
WHERE city = @city
  AND ts >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL @days DAY)
ORDER BY ts
"""

@st.cache_data(ttl=300, show_spinner=True)
def load_data(query: str, city_param: str, days_param: int) -> pd.DataFrame:
    job = bq.query(
        query,
        job_config=bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("city", "STRING", city_param),
                bigquery.ScalarQueryParameter("days", "INT64", days_param),
            ]
        ),
    )
    df = job.result().to_dataframe()  # nécessite db-dtypes/pyarrow
    return df

# --- Chargement ---
try:
    df = load_data(sql, city, days)
except Exception as e:
    st.error(f"Échec de chargement BigQuery : {e}")
    st.stop()

if df.empty:
    st.info("Aucune donnée pour cette plage. Lance une ingestion (Scheduler) et réessaie.")
    st.stop()

# --- Préparation des données ---
if not pd.api.types.is_datetime64_any_dtype(df["ts"]):
    df["ts"] = pd.to_datetime(df["ts"], utc=True).dt.tz_convert(None)
df = df.sort_values("ts").set_index("ts")

# --- KPIs rapides ---
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Température moyenne (°C)", f"{df['temperature_2m'].mean():.1f}")
with k2:
    st.metric("Humidité relative moyenne (%)", f"{df['relative_humidity_2m'].mean():.0f}")
with k3:
    st.metric("Précipitations totales (mm)", f"{df['precipitation'].sum():.1f}")
with k4:
    st.metric("Vent moyen (km/h)", f"{df['wind_speed_10m'].mean():.1f}")

st.markdown(f"### Évolution des dernières {days} journée(s) – {city}")

# --- Graphiques avec titres au-dessus ---
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Température (°C)")
    st.line_chart(df[["temperature_2m"]], height=260, use_container_width=True)

with col2:
    st.markdown("#### Humidité relative (%)")
    st.line_chart(df[["relative_humidity_2m"]], height=260, use_container_width=True)

with col1:
    st.markdown("#### Précipitations (mm)")
    st.bar_chart(df[["precipitation"]], height=260, use_container_width=True)

with col2:
    st.markdown("#### Vitesse du vent (km/h)")
    st.line_chart(df[["wind_speed_10m"]], height=260, use_container_width=True)

# --- Tableau de détails ---
st.markdown("### Détails horaires")
st.dataframe(
    df.reset_index().rename(
        columns={
            "ts": "timestamp",
            "temperature_2m": "temp_°C",
            "relative_humidity_2m": "humid_%",
            "precipitation": "pluie_mm",
            "wind_speed_10m": "vent_km_h",
        }
    ).tail(300),
    use_container_width=True,
)
