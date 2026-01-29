import os
from dotenv import load_dotenv

from extract import extract_matches
from transform import clean_match_data, split_players
from load import load_data_to_postgres

def make_db_url() -> str:
    user = os.environ["POSTGRES_USER"]
    pwd  = os.environ["POSTGRES_PASSWORD"]
    port = os.environ.get("POSTGRES_PORT", "5432")
    db   = os.environ["POSTGRES_DB"]

    # 1 seul .env : localhost par défaut, db dans Docker
    host = os.environ.get("POSTGRES_HOST", "localhost")
    if os.path.exists("/.dockerenv"):
        host = "db"

    return f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}"

def main():
    load_dotenv()

    print("🔽 Extraction")
    df_raw = extract_matches("data/atp_matches_2024.csv")
    print(f"Rows raw: {len(df_raw)}")

    print("🧹 Transformation")
    df_clean = clean_match_data(df_raw)
    print(f"Rows clean: {len(df_clean)}")

    print("👥 Split players + ids")
    players_df, matches_df = split_players(df_clean)
    print(f"Players: {len(players_df)} | Matches: {len(matches_df)}")

    print("📦 Chargement DB")
    db_url = make_db_url()
    load_data_to_postgres(players_df[["player_id", "name"]], matches_df, db_url)

    print("✅ ETL terminé")

if __name__ == "__main__":
    main()