import os
import logging
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
logging.getLogger('tensorflow').setLevel(logging.ERROR)

import streamlit as st
import pandas as pd
import tensorflow as tf
import joblib

MODEL_PATH = "models/model.keras"
PREPROCESSOR_PATH = "models/model.keras_preprocessor.pkl"

st.set_page_config(page_title="Game Price Predictor", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

* { font-family: 'Inter', sans-serif; }

/* ── Background ── */
.stApp {
    background: #07071a;
    background-image:
        radial-gradient(ellipse 100% 60% at 50% -10%, rgba(109,40,217,0.55) 0%, rgba(109,40,217,0.15) 40%, transparent 70%),
        radial-gradient(ellipse 50% 40% at 90% 90%, rgba(6,182,212,0.20) 0%, transparent 55%),
        radial-gradient(ellipse 40% 30% at 10% 80%, rgba(124,58,237,0.12) 0%, transparent 50%);
}

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem !important; padding-bottom: 2rem !important;
                   padding-left: 16rem !important; padding-right: 16rem !important; }

/* ── Gap between columns ── */
[data-testid="stHorizontalBlock"] { gap: 1.5rem; }

/* ── Hero header ── */
.hero { text-align: center; padding: 2.5rem 1rem 2rem; }
.hero-icon {
    width: 80px; height: 80px; margin: 0 auto 1.1rem;
    background: linear-gradient(135deg, #7c3aed, #06b6d4);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 0 28px rgba(124,58,237,0.7), 0 0 70px rgba(6,182,212,0.3);
}
.hero h1 {
    font-size: 2.4rem; font-weight: 800; margin: 0;
    background: linear-gradient(90deg, #a78bfa, #06b6d4);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero p { color: #94a3b8; font-size: 1rem; margin-top: 0.5rem; font-weight: 300; }

/* ── Card ── */
.card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(124,58,237,0.25);
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    height: 100%;
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 24px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.06);
}
.card-title {
    color: #a78bfa; font-size: 0.75rem; font-weight: 600; text-align: center;
    letter-spacing: 0.12em; text-transform: uppercase; margin-top: 0; margin-bottom: 0.75rem;
}

/* ── Suppress Streamlit's extra bottom spacing inside cards ── */
[data-testid="column"] [data-testid="stVerticalBlock"] > div:last-child { margin-bottom: 0 !important; }
[data-testid="column"] .element-container:last-of-type { margin-bottom: 0 !important; }
[data-testid="column"] > div { padding-bottom: 0 !important; }

/* ── Labels ── */
.stSelectbox label, .stSlider label, .stSelectSlider label, .stToggle label {
    color: #cbd5e1 !important; font-size: 0.85rem !important; font-weight: 500 !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(124,58,237,0.35) !important;
    border-radius: 10px !important;
    color: #f1f5f9 !important;
}
.stSelectbox > div > div:focus-within {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.25) !important;
}

/* ── Slider track ── */
.stSlider [data-baseweb="slider"] [data-testid="stSliderTrack"] div:first-child {
    background: linear-gradient(90deg, #7c3aed, #06b6d4) !important;
}
.stSlider [data-baseweb="slider"] [role="slider"] {
    background: #7c3aed !important;
    box-shadow: 0 0 10px rgba(124,58,237,0.8) !important;
}

/* ── Button ── */
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #7c3aed 0%, #06b6d4 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.6rem 1.5rem !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.04em !important;
    box-shadow: 0 0 20px rgba(124,58,237,0.5), 0 4px 15px rgba(0,0,0,0.3) !important;
    transition: all 0.2s ease !important;
    margin-top: 0.4rem;
}
.stButton > button:hover {
    box-shadow: 0 0 35px rgba(124,58,237,0.75), 0 4px 20px rgba(6,182,212,0.4) !important;
    transform: translateY(-1px) !important;
}

/* ── Result box ── */
.result-box {
    background: linear-gradient(135deg, rgba(124,58,237,0.15), rgba(6,182,212,0.10));
    border: 1px solid rgba(124,58,237,0.5);
    border-radius: 16px;
    padding: 0.75rem;
    text-align: center;
    margin-top: 0.5rem;
    box-shadow: 0 0 40px rgba(124,58,237,0.2), inset 0 1px 0 rgba(255,255,255,0.08);
}
.result-label {
    color: #94a3b8; font-size: 0.72rem; font-weight: 600;
    letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 0.25rem;
}
.result-price {
    font-size: 2.2rem; font-weight: 800;
    background: linear-gradient(90deg, #a78bfa, #06b6d4);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    line-height: 1.1;
}
.result-sub { color: #64748b; font-size: 0.75rem; margin-top: 0.25rem; }

/* ── Separator ── */
.separator {
    border: none;
    border-top: 1px solid rgba(124,58,237,0.25);
    margin: 2rem 0 1.25rem;
}

/* ── Error ── */
.stAlert { border-radius: 12px !important; border-left-color: #7c3aed !important; }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_model():
    preprocessor = joblib.load(PREPROCESSOR_PATH)
    model = tf.keras.models.load_model(MODEL_PATH)
    return preprocessor, model


# ── Hero ──
st.markdown("""
<div class="hero">
    <div class="hero-icon">
        <svg width="42" height="42" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg">
            <!-- Manette stylisée -->
            <rect x="6" y="13" width="30" height="18" rx="9" fill="none" stroke="white" stroke-width="2"/>
            <!-- Croix directionnelle gauche -->
            <rect x="12" y="19.5" width="6" height="2" rx="1" fill="white"/>
            <rect x="14.5" y="17" width="2" height="6" rx="1" fill="white"/>
            <!-- Boutons droite -->
            <circle cx="28" cy="20" r="1.5" fill="white" opacity="0.6"/>
            <circle cx="31" cy="22.5" r="1.5" fill="white"/>
            <circle cx="28" cy="25" r="1.5" fill="white" opacity="0.6"/>
            <circle cx="25" cy="22.5" r="1.5" fill="white" opacity="0.6"/>
            <!-- Boutons centraux -->
            <rect x="19" y="21.5" width="2" height="2" rx="0.5" fill="white" opacity="0.5"/>
            <rect x="22" y="21.5" width="2" height="2" rx="0.5" fill="white" opacity="0.5"/>
        </svg>
    </div>
    <h1>Game Price Predictor</h1>
    <p>AI-powered predictions &nbsp;·&nbsp; Deep Learning</p>
</div>
""", unsafe_allow_html=True)

platform = "PC"

col1, col2, col3 = st.columns(3)

# ── Col 1 : Game ──
with col1:
    st.markdown('<div class="card"><div class="card-title">Game</div>', unsafe_allow_html=True)
    genre          = st.selectbox("Genre", ["Action", "Adventure", "RPG", "Racing", "Simulation", "Sports", "Strategy"])
    developer_size = st.selectbox("Developer size", ["indie", "AA", "AAA"])
    st.markdown('</div>', unsafe_allow_html=True)

# ── Col 2 : Score & Popularity ──
with col2:
    st.markdown('<div class="card"><div class="card-title">Score & Popularity</div>', unsafe_allow_html=True)
    user_score       = st.slider("User score (0-10)", min_value=0.0, max_value=10.0, value=7.0, step=0.1)
    review_count_raw = st.select_slider(
        "Number of reviews",
        options=[50, 500, 5_000, 50_000, 500_000, 5_000_000],
        value=5_000,
        format_func=lambda x: f"{x:,}",
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ── Col 3 : Gameplay ──
with col3:
    st.markdown('<div class="card"><div class="card-title">Gameplay</div>', unsafe_allow_html=True)
    game_duration_hours = st.slider("Game duration (hours)", min_value=1, max_value=150, value=20)
    has_online          = int(st.toggle("Online multiplayer", value=False))
    st.markdown('</div>', unsafe_allow_html=True)

# ── Bottom bar : Predict ──
st.markdown('<hr class="separator">', unsafe_allow_html=True)
if st.button("Predict price"):
    try:
        import math
        preprocessor, model = load_model()
        input_df = pd.DataFrame([{
            "platform":            platform,
            "genre":               genre,
            "developer_size":      developer_size,
            "user_score":          user_score,
            "log_review_count":    round(math.log1p(review_count_raw), 4),
            "game_duration_hours": game_duration_hours,
            "has_online":          has_online,
        }])
        X_processed = preprocessor.transform(input_df)
        prediction  = model.predict(X_processed, verbose=0).flatten()[0]

        st.markdown(f"""
        <div class="result-box">
            <div class="result-label">Estimated sale price</div>
            <div class="result-price">${prediction:.2f}</div>
            <div class="result-sub">{genre} &nbsp;·&nbsp; {developer_size}</div>
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Prediction error : {e}")
