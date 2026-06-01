# Game Price Predictor

A Machine Learning project using Deep Learning (TensorFlow) to **predict the sale price of PC games on Steam** based on features such as genre, developer size, user score, playtime, and popularity.

An interactive web interface is available via Streamlit.

## Installation

### 1. Create the virtual environment

Run the setup script once (Git Bash):

```bash
bash setup_env.sh
```

This will create a `venv/` virtual environment and install all dependencies automatically.

To activate the environment in future sessions:

```bash
source venv/Scripts/activate
```

### 2. Manual install (optional)

```bash
pip install -r requirements.txt
```

## Web Interface (Streamlit)

Launch the interactive interface to make predictions:

```bash
streamlit run app.py
```

The interface lets you input a game's characteristics (genre, developer size, user score, playtime, number of reviews, player count, online multiplayer) and instantly get an estimated sale price.

## Data Collection (SteamSpy API)

Game data is collected from the [SteamSpy API](https://steamspy.com/api.php) — no API key required.

```bash
python scripts/fetch_data.py --target 500 --output data/raw/raw_data.csv
```

Runtime is approximately 3 minutes. The script works in two steps:

1. **SteamSpy bulk** (`request=all`) — fetches 3000 popular games in 3 requests, filters paid games only, sorts by popularity.
2. **SteamSpy appdetails** — fetches genre and tags for the top entries concurrently (5 workers, rate-limited).

Only paid games (`price > 0`) with at least 50 reviews and a recognised genre are kept.

Features collected:

| Feature | Source |
|---|---|
| `title` | Game name |
| `platform` | PC (Steam) |
| `genre` | SteamSpy genre tags |
| `developer_size` | Publisher name heuristic (indie / AA / AAA) |
| `user_score` | Positive reviews / total reviews × 10 |
| `log_review_count` | log(1 + total reviews) — popularity proxy |
| `player_count` | Derived from SteamSpy multiplayer tags |
| `game_duration_hours` | Average playtime in hours (SteamSpy) |
| `has_online` | Derived from SteamSpy multiplayer tags |
| `target` | Current Steam price in USD |

## Command-line Pipeline

Run the full pipeline with:

```bash
bash run_pipeline.sh
```

Or step by step:

### 1. Data Collection

```bash
python scripts/fetch_data.py --target 500 --output data/raw/raw_data.csv
```

### 2. Data Preparation

```bash
python scripts/prep_data.py \
  --input data/raw/raw_data.csv \
  --output data/processed/processed_data.csv
```

### 3. Model Training

```bash
python scripts/train_model.py \
  --data data/processed/processed_data.csv \
  --model_output models/model.keras
```

Automatically saves:

- the TensorFlow model `model.keras`
- the preprocessor `model.keras_preprocessor.pkl`

### 4. Prediction

```bash
python scripts/predict.py \
  --input data/processed/processed_data.csv \
  --model models/model.keras \
  --output outputs/predictions.csv
```

The script appends a `predicted_price` column to the CSV.

### 5. Evaluation (if the target column is present)

```bash
python scripts/evaluate.py \
  --input outputs/predictions.csv
```

Outputs:

- MAE (Mean Absolute Error)
- RMSE (Root Mean Squared Error)
- R² score (coefficient of determination)

## Tech Stack

- Python 3.10+
- TensorFlow / Keras
- Scikit-learn
- Pandas / NumPy
- Joblib
- Streamlit
- SteamSpy API
