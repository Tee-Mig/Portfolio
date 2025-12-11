from fastapi import FastAPI, Response
import os, json, datetime as dt, requests, pathlib, base64
from google.cloud import storage, pubsub_v1
import yaml

app = FastAPI()
GCS_BUCKET = os.getenv("RAW_BUCKET")          # ex: weather-raw-<id>
PUBSUB_TOPIC = os.getenv("PUBSUB_TOPIC")      # ex: projects/<proj>/topics/transform
OPENMETEO_URL = "https://api.open-meteo.com/v1/forecast"

def load_cities():
    with open("/app/cities.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["cities"]

def gcs_path_now():
    now = dt.datetime.utcnow()
    return f"raw/{now:%Y/%m/%d/%H}/payload.json"

@app.get("/")
def health():
    return {"ok": True}

@app.post("/run")
def run():
    cities = load_cities()
    payload = []
    for c in cities:
        params = {
            "latitude": c["lat"], "longitude": c["lon"],
            "hourly": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
            "timezone": "UTC",
        }
        r = requests.get(OPENMETEO_URL, params=params, timeout=20)
        r.raise_for_status()
        js = r.json(); js["city"] = c["name"]
        payload.append(js)

    # Save raw to GCS
    client = storage.Client()
    blob = client.bucket(GCS_BUCKET).blob(gcs_path_now())
    blob.upload_from_string(json.dumps(payload), content_type="application/json")

    # Notify transformer via Pub/Sub (optional in Step 2)
    if PUBSUB_TOPIC:
        pub = pubsub_v1.PublisherClient()
        # Put only the GCS path in attributes; auth is via Authorization header added by the push subscription
        future = pub.publish(
            PUBSUB_TOPIC,
            b"transform",           # small body is fine
            path=blob.name          # attribute used by transformer to locate the raw file
        )
        future.result(timeout=10)

    return {"status": "ok", "stored": blob.name}
