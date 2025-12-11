import base64, json, os
from typing import List, Dict, Any
from dateutil import parser as dtparse
from fastapi import FastAPI, Request, Response
from google.cloud import storage, bigquery

app = FastAPI()
PROJECT_ID = os.getenv("PROJECT_ID")
DATASET = os.getenv("BQ_DATASET", "weather")
TABLE   = os.getenv("BQ_TABLE", "observations")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")  # shared secret to validate push

# GCS/BQ clients
_gcs = storage.Client()
_bq  = bigquery.Client()

def _rows_from_payload(item: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Flatten one city payload from Open-Meteo into row dicts."""
    city = item.get("city")
    h = item.get("hourly", {}) or {}
    times = h.get("time", []) or []
    temps = h.get("temperature_2m", []) or []
    rh    = h.get("relative_humidity_2m", []) or []
    pr    = h.get("precipitation", []) or []
    ws    = h.get("wind_speed_10m", []) or []
    n = len(times)
    out = []
    for i in range(n):
        ts = dtparse.isoparse(times[i])  # ISO8601 -> datetime
        out.append({
            "city": city,
            "ts": ts.isoformat(),
            "temperature_2m": float(temps[i]) if i < len(temps) else None,
            "relative_humidity_2m": float(rh[i]) if i < len(rh) else None,
            "precipitation": float(pr[i]) if i < len(pr) else None,
            "wind_speed_10m": float(ws[i]) if i < len(ws) else None
        })
    return out

def _load_from_gcs(bucket: str, path: str) -> List[Dict[str, Any]]:
    blob = _gcs.bucket(bucket).blob(path)
    data = blob.download_as_bytes()
    return json.loads(data)

def _insert_rows(rows: List[Dict[str, Any]]):
    table_id = f"{PROJECT_ID}.{DATASET}.{TABLE}"
    errors = _bq.insert_rows_json(table_id, rows)
    if errors:
        raise RuntimeError(f"BigQuery insert errors: {errors}")

@app.post("/process")
async def process(request: Request):
    # Pub/Sub push validation
    if WEBHOOK_SECRET:
        auth = request.headers.get("authorization", "")
        if auth != f"Bearer {WEBHOOK_SECRET}":
            return Response("forbidden", status_code=403)

    body = await request.json()
    msg = body.get("message", {})
    # attributes: path to GCS blob
    attributes = msg.get("attributes") or {}
    path = attributes.get("path")
    if not path:
        # fallback: data base64 with {"path": "..."}
        data_b64 = msg.get("data")
        if data_b64:
            try:
                decoded = json.loads(base64.b64decode(data_b64).decode("utf-8"))
                path = decoded.get("path")
            except Exception:
                pass
    if not path:
        return Response("missing path", status_code=400)

    bucket = os.getenv("RAW_BUCKET")  # not strictly needed, but handy
    if not bucket:
        return Response("RAW_BUCKET not set", status_code=500)

    # Load, transform, write
    payload = _load_from_gcs(bucket, path)
    # payload is a list of city objects
    rows = []
    for item in payload:
        rows.extend(_rows_from_payload(item))

    # Insert in batches to avoid large payloads
    BATCH = 500
    for i in range(0, len(rows), BATCH):
        _insert_rows(rows[i:i+BATCH])

    return {"status": "ok", "rows": len(rows), "table": f"{PROJECT_ID}.{DATASET}.{TABLE}"}
