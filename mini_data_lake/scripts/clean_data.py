import pandas as pd
from pathlib import Path

input_path = Path("data/raw/air_pollution_raw.csv")
output_path = Path("data/clean/air_pollution_clean.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(input_path)

df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df.dropna(subset=["city", "country", "date", "pm25"])
df = df[df["pm25"] >= 0]

def classify_pm25(value):
    if value <= 12:
        return "Good"
    elif value <= 35.4:
        return "Moderate"
    elif value <= 55.4:
        return "Unhealthy for Sensitive Groups"
    else:
        return "Unhealthy"

df["pm25_category"] = df["pm25"].apply(classify_pm25)

df.to_csv(output_path, index=False)
print(f"[✔] Données nettoyées sauvegardées dans {output_path}")