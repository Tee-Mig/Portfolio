"""
Fetches real Steam game data in ~3 minutes.

Strategy:
  1. SteamSpy bulk API (3 requests) -> 3000 entries, filter paid games -> ~2300 app IDs
  2. SteamSpy individual appdetails for top 600 IDs (sorted by popularity)
     - genre and tags only available in individual endpoint
     - 5 concurrent workers, 0.3s global rate limit -> ~3 min

Usage:
    python scripts/fetch_data.py --target 500 --output data/raw/raw_data.csv
"""
import os
import math
import time
import logging
import argparse
import threading
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger(__name__)

MAJOR_PUBLISHERS = {
    "Electronic Arts", "EA Games", "Ubisoft", "Activision", "Blizzard Entertainment",
    "Bethesda Softworks", "Rockstar Games", "2K", "Square Enix", "Bandai Namco",
    "SEGA", "Capcom", "Konami", "Koei Tecmo", "Koch Media", "THQ Nordic",
    "Deep Silver", "Focus Home Interactive", "Warner Bros.", "Microsoft Studios",
    "Sony Interactive Entertainment", "Nintendo",
}

GENRE_MAP = {
    "Action": "Action", "Adventure": "Adventure", "RPG": "RPG",
    "Strategy": "Strategy", "Simulation": "Simulation",
    "Sports": "Sports", "Racing": "Racing",
}

ONLINE_TAGS = {"Multiplayer", "Online Co-Op", "PvP", "Online PvP",
               "Massively Multiplayer", "Co-op", "Online"}

# --- Rate limiter ---
_last_call = 0.0
_rate_lock  = threading.Lock()
MIN_INTERVAL = 0.3

def _get(url):
    global _last_call
    with _rate_lock:
        wait = MIN_INTERVAL - (time.time() - _last_call)
        if wait > 0:
            time.sleep(wait)
        _last_call = time.time()
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    return r.json()


# --- Step 1: bulk fetch, filter paid games ---

def get_paid_app_ids(n_pages=3):
    ids_with_price = []
    log.info("Fetching SteamSpy bulk data...")
    for page in range(n_pages):
        r = requests.get(
            f"https://steamspy.com/api.php?request=all&page={page}",
            timeout=20,
        )
        r.raise_for_status()
        data = r.json()
        for appid, entry in data.items():
            try:
                price    = int(entry.get("price", 0) or 0)
                positive = int(entry.get("positive", 0) or 0)
            except (ValueError, TypeError):
                continue
            if 0 < price <= 12000:
                ids_with_price.append((appid, positive))
        log.info(f"  Page {page}: total paid games: {len(ids_with_price)}")
        time.sleep(1.5)

    # Sort by popularity (most reviews first) for best coverage
    ids_with_price.sort(key=lambda x: x[1], reverse=True)
    return [int(appid) for appid, _ in ids_with_price]


# --- Step 2: individual appdetails ---

def fetch_appdetails(appid):
    return _get(f"https://steamspy.com/api.php?request=appdetails&appid={appid}")


def parse_genre(genre_str):
    if not genre_str:
        return None
    for part in genre_str.split(","):
        g = part.strip()
        if g in GENRE_MAP:
            return GENRE_MAP[g]
    return None


def parse(entry):
    try:
        price = int(entry.get("price", 0) or 0)
    except (ValueError, TypeError):
        return None
    if price <= 0 or price > 12000:
        return None

    genre_str  = entry.get("genre", "") or ""
    main_genre = parse_genre(genre_str)
    if not main_genre:
        return None

    positive = int(entry.get("positive", 0) or 0)
    negative = int(entry.get("negative", 0) or 0)
    if positive + negative < 50:
        return None

    user_score    = round(positive / (positive + negative) * 10, 2)
    log_reviews   = round(math.log1p(positive + negative), 4)

    avg_min = int(entry.get("average_forever", 0) or 0)
    game_duration = max(1, round(avg_min / 60, 1)) if avg_min > 0 else 10.0

    tags       = entry.get("tags") or {}
    has_online = 1 if any(t in ONLINE_TAGS for t in tags) else 0

    publisher = (entry.get("publisher") or "").strip()
    if publisher in MAJOR_PUBLISHERS:
        developer_size = "AAA"
    elif "Indie" in genre_str:
        developer_size = "indie"
    else:
        developer_size = "AA"

    return {
        "title":               entry.get("name", "Unknown"),
        "platform":            "PC",
        "genre":               main_genre,
        "developer_size":      developer_size,
        "user_score":          user_score,
        "log_review_count":    log_reviews,
        "game_duration_hours": game_duration,
        "has_online":          int(has_online),
        "target":              round(price / 100, 2),
    }


def fetch_and_parse(appid):
    try:
        return parse(fetch_appdetails(appid))
    except Exception as e:
        log.debug(f"Failed appid {appid}: {e}")
        return None


# --- Main ---

def main(args):
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    app_ids = get_paid_app_ids(n_pages=3)
    log.info(f"{len(app_ids)} paid game IDs found, fetching top {args.target + 100} individually...")

    t0    = time.time()
    games = []
    ids_to_fetch = app_ids[:args.target + 100]

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(fetch_and_parse, appid): appid for appid in ids_to_fetch}
        for future in as_completed(futures):
            if len(games) >= args.target:
                break
            row = future.result()
            if row:
                games.append(row)
                log.info(f"[{len(games):>3}/{args.target}] {row['title']} — ${row['target']:.2f}"
                         f"  ({row['genre']}, {row['developer_size']})  [{time.time()-t0:.0f}s]")
                if len(games) % 50 == 0:
                    pd.DataFrame(games).to_csv(args.output, index=False)
                    log.info(f"  Progress saved ({len(games)} games)")

    df = pd.DataFrame(games)
    if df.empty:
        log.error("No games collected.")
        return

    df = df.drop_duplicates(subset="title").reset_index(drop=True)
    df.to_csv(args.output, index=False)
    log.info(f"\nDone — {len(df)} games saved to {args.output} in {time.time()-t0:.0f}s")
    print(df.describe())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch Steam game data via SteamSpy")
    parser.add_argument("--target", type=int, default=500)
    parser.add_argument("--output", type=str, default="data/raw/raw_data.csv")
    args = parser.parse_args()
    main(args)
