# dashboard/app.py
from __future__ import annotations

from pathlib import Path
import importlib.util

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt


# ============================================================
# Page + Style (dark / neon dashboard)
# ============================================================
st.set_page_config(page_title="RL Snake Analytics", layout="wide")

st.markdown(
    """
<style>
/* ---- Background ---- */
.stApp {
  background: radial-gradient(1200px 600px at 20% 0%, rgba(123,97,255,0.20), transparent 60%),
              radial-gradient(900px 500px at 90% 10%, rgba(64,224,208,0.16), transparent 55%),
              radial-gradient(900px 700px at 40% 100%, rgba(255,105,180,0.14), transparent 55%),
              linear-gradient(180deg, #0B0D16 0%, #070811 100%);
  color: #EAEAF2;
}

/* ---- Typography ---- */
h1, h2, h3, h4, h5 { color: #F4F5FF; letter-spacing: 0.2px; }
small, .stCaption { color: rgba(234,234,242,0.70) !important; }

/* ---- Sidebar ---- */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0.01) 100%);
  border-right: 1px solid rgba(255,255,255,0.08);
}

[data-testid="stSidebar"] h2 {
  font-size: 2rem !important;
  font-weight: 700;
  margin-bottom: 0.4rem;
}

/* ---- “Card” containers ---- */
.card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 18px;
  padding: 16px 18px;
  box-shadow: 0 10px 24px rgba(0,0,0,0.35);

  min-height: 120px;      /* a bit taller so text can breathe */
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.card h3 { margin: 0 0 8px 0; font-size: 19px; }
.card p {
  margin: 0;
  color: rgba(234,234,242,0.80);
  font-size: 15px;        /* bigger value text */

  /* clamp 2 lines so it stays readable on small windows */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* ---- Dataframe ---- */
[data-testid="stDataFrame"] {
  background: rgba(255,255,255,0.02);
  border-radius: 14px;
  border: 1px solid rgba(255,255,255,0.08);
  overflow: hidden;
}

/* ---- Metrics ---- */
[data-testid="stMetric"] {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 18px;
  padding: 14px 14px;

  height: 120px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
[data-testid="stMetricLabel"] { color: rgba(234,234,242,0.75) !important; }
[data-testid="stMetricValue"] { color: #F4F5FF !important; }
[data-testid="stMetricDelta"] { color: rgba(234,234,242,0.75) !important; }

/* ---- Buttons / inputs ---- */
.stButton>button {
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.14);
  background: rgba(255,255,255,0.04);
  color: #F4F5FF;
}
.stTextInput>div>div>input, .stSelectbox>div>div, .stMultiSelect>div>div {
  border-radius: 12px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.10);
}

/* ---- Hide Streamlit footer ---- */
footer { visibility: hidden; }
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# Header
# ============================================================
st.title("RL Snake — Training Analytics")
st.caption(
    "Dashboard de suivi d'entraînement DQN. "
    "Lecture de métriques depuis des fichiers .parquet / .csv dans ./runs."
)


# ============================================================
# Helpers
# ============================================================
def find_metric_files(runs_dir: Path) -> list[Path]:
    patterns = [
        "**/metrics_*.parquet",
        "**/metrics.parquet",
        "**/*.parquet",
        "**/metrics_*.csv",
        "**/metrics.csv",
        "**/*.csv",
    ]
    if not runs_dir.exists():
        return []
    files: list[Path] = []
    seen = set()
    for pat in patterns:
        for p in runs_dir.glob(pat):
            if p.is_file():
                rp = p.resolve()
                if rp not in seen:
                    files.append(p)
                    seen.add(rp)
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files


def parquet_engine_status() -> str:
    pyarrow_ok = importlib.util.find_spec("pyarrow") is not None
    fastparquet_ok = importlib.util.find_spec("fastparquet") is not None
    if pyarrow_ok:
        return "pyarrow ✅"
    if fastparquet_ok:
        return "fastparquet ✅"
    return "Aucun moteur parquet (installe pyarrow) ⚠️"


@st.cache_data
def load_metrics(path: Path) -> pd.DataFrame:
    if path.suffix == ".parquet":
        df = pd.read_parquet(path)
    elif path.suffix == ".csv":
        df = pd.read_csv(path)
    else:
        raise ValueError("Unsupported file type. Use .parquet or .csv")

    df = df.loc[:, ~df.columns.str.contains(r"^Unnamed")]

    if "episode" not in df.columns:
        df.insert(0, "episode", range(len(df)))

    for col in ["episode", "reward", "length", "steps", "epsilon", "phase", "playable_grid", "loss"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.sort_values("episode").reset_index(drop=True)
    return df


def rolling(s: pd.Series, w: int) -> pd.Series:
    return s.rolling(window=w, min_periods=1).mean()


# ---- Matplotlib ----
def fig_dark():
    fig = plt.figure(figsize=(9.6, 5.2))
    ax = plt.gca()

    fig.patch.set_facecolor((0, 0, 0, 0))
    ax.set_facecolor((0, 0, 0, 0))

    ax.grid(color=(1, 1, 1, 0.20), linewidth=1.2)

    for spine in ax.spines.values():
        spine.set_color((1, 1, 1, 0.45))
        spine.set_linewidth(1.2)

    ax.tick_params(colors=(1, 1, 1, 0.85), labelsize=11)
    ax.xaxis.label.set_color((1, 1, 1, 0.85))
    ax.yaxis.label.set_color((1, 1, 1, 0.85))
    ax.title.set_color((1, 1, 1, 0.95))
    return fig, ax


# ============================================================
# Sidebar: source + controls
# ============================================================
runs_dir = Path("runs")
files = find_metric_files(runs_dir)

st.sidebar.header("RL Snake")

manual_path = st.sidebar.text_input(
    "Chemin manuel",
    value="",
    help="Ex: runs/run_2026/metrics.parquet ou runs/metrics.csv",
)

metrics_path: Path | None = None
if manual_path.strip():
    p = Path(manual_path.strip())
    if p.exists() and p.is_file():
        metrics_path = p
    else:
        st.sidebar.error("Chemin manuel invalide / introuvable.")
else:
    if not files:
        st.error("Aucun fichier .parquet/.csv trouvé dans ./runs (ni sous-dossiers).")
        st.stop()

    labels = []
    for p in files:
        rel = p.as_posix()
        mtime = pd.to_datetime(p.stat().st_mtime, unit="s")
        labels.append(f"{rel}  —  modifié {mtime.strftime('%Y-%m-%d %H:%M:%S')}")

    choice = st.sidebar.selectbox("Choisir un fichier", labels, index=0)
    metrics_path = files[labels.index(choice)]

if metrics_path is None:
    st.stop()

df = load_metrics(metrics_path)
st.sidebar.caption(f"Chargé: {metrics_path.as_posix()}")

# Controls
st.sidebar.header("⚙️ Contrôles")
window = st.sidebar.slider("Fenêtre moyenne par episodes", 10, 500, 100, 10)
show_raw = st.sidebar.checkbox("Afficher la courbe brute", value=True)

ep_min, ep_max = int(df["episode"].min()), int(df["episode"].max())
selected_range = st.sidebar.slider("Plage d'épisodes", ep_min, ep_max, (ep_min, ep_max))
df_view = df[(df["episode"] >= selected_range[0]) & (df["episode"] <= selected_range[1])].copy()

# Optional filters
if "phase" in df_view.columns:
    st.sidebar.subheader("Filtres")
    phases = sorted([int(x) for x in df["phase"].dropna().unique()])
    if phases:
        phase_choice = st.sidebar.multiselect("Phases", phases, default=phases)
        df_view = df_view[df_view["phase"].isin(phase_choice)]

if "playable_grid" in df_view.columns:
    grids = sorted([int(x) for x in df["playable_grid"].dropna().unique()])
    if grids:
        grid_choice = st.sidebar.multiselect("Playable grid", grids, default=grids)
        df_view = df_view[df_view["playable_grid"].isin(grid_choice)]

for col in ["reward", "length", "steps"]:
    if col in df_view.columns:
        df_view[f"{col}_moy"] = rolling(df_view[col], window)
if "loss" in df_view.columns:
    df_view["loss_moy"] = rolling(df_view["loss"], window)


# ============================================================
# KPIs + cards
# ============================================================
if len(df_view) == 0:
    st.warning("Aucune donnée dans la plage/filtres sélectionnés.")
    st.stop()

best_row = df_view.loc[df_view["reward"].idxmax()] if "reward" in df_view.columns else df_view.iloc[-1]
last_row = df_view.iloc[-1]

k1, k2, k3, k4 = st.columns(4)
k1.metric("Épisodes (sélection)", f"{len(df_view):,}")
k2.metric(
    "Meilleur reward",
    f"{best_row['reward']:.1f}" if "reward" in df_view.columns else "N/A",
    help=f"Episode {int(best_row['episode'])}" if "reward" in df_view.columns else None,
)
k3.metric("Meilleure longueur", f"{df_view['length'].max():.0f}" if "length" in df_view.columns else "N/A")
k4.metric("Epsilon (dernier)", f"{last_row['epsilon']:.3f}" if "epsilon" in df_view.columns else "N/A")

c1, c2, c3 = st.columns(3)
source_short = metrics_path.name
with c1:
    st.markdown(
        f"""
<div class="card">
  <h3>Source</h3>
  <p title="{metrics_path.as_posix()}">{source_short}</p>
</div>
""",
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        f"""
<div class="card">
  <h3>Episodes</h3>
  <p>{int(df_view["episode"].min()):,} → {int(df_view["episode"].max()):,}</p>
</div>
""",
        unsafe_allow_html=True,
    )
with c3:
    max_len = int(df_view["length"].max()) if "length" in df_view.columns else None
    st.markdown(
        f"""
<div class="card">
  <h3>Max length</h3>
  <p>{max_len if max_len is not None else "N/A"}</p>
</div>
""",
        unsafe_allow_html=True,
    )

st.divider()


# ============================================================
# Charts
# ============================================================
left, right = st.columns(2)

with left:
    st.subheader("📈 Reward par épisode")
    if "reward" in df_view.columns:
        fig, ax = fig_dark()
        if show_raw:
            ax.plot(df_view["episode"], df_view["reward"], linewidth=1.2, alpha=0.35, label="reward")
        ax.plot(df_view["episode"], df_view["reward_moy"], linewidth=2.6, label=f"moy({window})")
        ax.set_xlabel("Episode")
        ax.set_ylabel("Reward")
        ax.legend(frameon=False, labelcolor=(1, 1, 1, 0.85), fontsize=11)
        st.pyplot(fig, clear_figure=True)
    else:
        st.info("Colonne 'reward' absente.")

with right:
    st.subheader("📏 Longueur du snake par épisode")
    if "length" in df_view.columns:
        fig, ax = fig_dark()
        if show_raw:
            ax.plot(df_view["episode"], df_view["length"], linewidth=1.2, alpha=0.35, label="length")
        ax.plot(df_view["episode"], df_view["length_moy"], linewidth=2.6, label=f"moy({window})")
        ax.set_xlabel("Episode")
        ax.set_ylabel("Snake length")
        ax.legend(frameon=False, labelcolor=(1, 1, 1, 0.85), fontsize=11)
        st.pyplot(fig, clear_figure=True)
    else:
        st.info("Colonne 'length' absente.")

left2, right2 = st.columns(2)

with left2:
    st.subheader("Steps par épisode")
    if "steps" in df_view.columns:
        fig, ax = fig_dark()
        if show_raw:
            ax.plot(df_view["episode"], df_view["steps"], linewidth=1.2, alpha=0.35, label="steps")
        ax.plot(df_view["episode"], df_view["steps_moy"], linewidth=2.6, label=f"moy({window})")
        ax.set_xlabel("Episode")
        ax.set_ylabel("Steps")
        ax.legend(frameon=False, labelcolor=(1, 1, 1, 0.85), fontsize=11)
        st.pyplot(fig, clear_figure=True)
    else:
        st.info("Colonne 'steps' absente.")

with right2:
    st.subheader("Loss")
    if "loss" not in df_view.columns:
        st.info("La colonne 'loss' est absente.")
    else:
        loss_nonan = df_view.dropna(subset=["loss"])
        if len(loss_nonan) == 0:
            st.info("Loss uniquement NaN sur la plage sélectionnée.")
        else:
            fig, ax = fig_dark()
            if show_raw:
                ax.plot(loss_nonan["episode"], loss_nonan["loss"], linewidth=1.2, alpha=0.35, label="loss")
            ax.plot(loss_nonan["episode"], loss_nonan["loss_moy"], linewidth=2.6, label=f"moy({window})")
            ax.set_xlabel("Episode")
            ax.set_ylabel("Loss")
            ax.legend(frameon=False, labelcolor=(1, 1, 1, 0.85), fontsize=11)
            st.pyplot(fig, clear_figure=True)

st.divider()


# ============================================================
# Distributions + table
# ============================================================
colA, colB = st.columns(2)

with colA:
    st.subheader("Distribution des rewards")
    if "reward" in df_view.columns:
        fig, ax = fig_dark()
        ax.hist(df_view["reward"].dropna(), bins=40)
        ax.set_xlabel("Reward")
        ax.set_ylabel("Count")
        st.pyplot(fig, clear_figure=True)
    else:
        st.info("Colonne 'reward' absente.")

with colB:
    st.subheader("Distribution des longueurs")
    if "length" in df_view.columns:
        fig, ax = fig_dark()
        ax.hist(df_view["length"].dropna(), bins=40)
        ax.set_xlabel("Snake length")
        ax.set_ylabel("Count")
        st.pyplot(fig, clear_figure=True)
    else:
        st.info("Colonne 'length' absente.")


st.subheader("Table des métriques")

table_colA, table_colB = st.columns([2, 3])
with table_colA:
    table_mode = st.radio("Afficher :", ["500 premiers épisodes", "500 derniers épisodes"], horizontal=True)

df_table = df_view.head(500) if table_mode == "500 premiers épisodes" else df_view.tail(500)

pretty_cols = {
    "episode": "Episode",
    "reward": "Reward total",
    "reward_moy": "Reward moyen (100 ep)",
    "length": "Longueur finale",
    "length_moy": "Longueur moyenne (100 ep)",
    "steps": "Steps (épisode)",
    "steps_moy": "Steps moyens (100 ep)",
    "epsilon": "Epsilon (exploration)",
    "loss": "TD Loss",
    "loss_moy": "TD Loss moyen (100 ep)",
    "phase": "Phase (curriculum)",
    "playable_grid": "Grid size",
}

st.dataframe(df_table.rename(columns=pretty_cols), use_container_width=True)
st.caption(f"Source: {metrics_path.as_posix()}")
