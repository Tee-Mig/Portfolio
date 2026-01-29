import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import os
import time
from dotenv import load_dotenv
from st_aggrid import AgGrid, GridOptionsBuilder

def wait_for_db(db_url: str, timeout: int = 30):
    """
    Attend que la base de données PostgreSQL soit prête à accepter les connexions.
    
    Args:
        db_url (str): URL de connexion SQLAlchemy.
        timeout (int): Temps maximal d'attente en secondes.
    """
    start_time = time.time()
    while True:
        try:
            engine = create_engine(db_url)
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            print("✅ Connexion à la base réussie.")
            break
        except OperationalError:
            if time.time() - start_time > timeout:
                raise Exception("❌ La base de données n'est pas accessible après 30 secondes.")
            print("⏳ Attente de la base de données...")
            time.sleep(2)

def display_stats():
    load_dotenv()

    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    db = os.getenv("POSTGRES_DB")

    db_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    
    wait_for_db(db_url)

    engine = create_engine(db_url)

    st.title("Tennis Stats Tracker")

    tab1, tab2 = st.tabs(["Joueurs", "Matchs"])

    with tab1:
        st.header("Liste des joueurs")
        try:
            st.header("Clique sur un joueur pour voir ses matchs")
            players_df = pd.read_sql(
                "SELECT name FROM players ORDER BY name",
                engine
            )

            search = st.text_input("🔎 Rechercher un joueur", "")
            if search.strip():
                players_filtered = players_df[players_df["name"].str.contains(search, case=False, na=False)]
            else:
                players_filtered = players_df

            matches_df = pd.read_sql("SELECT * FROM matches", engine)

            FR_COLS = {
                "tourney_id": "ID tournoi",
                "tourney_name": "Tournoi",
                "surface": "Surface",
                "tourney_level": "Niveau",
                "tourney_date": "Date",
                "round": "Tour",
                "score": "Score",
                "minutes": "Durée (min)",

                "winner_name": "Vainqueur",
                "loser_name": "Perdant",

                "winner_rank": "Classement vainqueur",
                "loser_rank": "Classement perdant",

                "w_ace": "Aces (vainqueur)",
                "w_df": "Doubles fautes (vainqueur)",
                "w_1stIn": "1res IN (vainqueur)",
                "w_1stWon": "1res gagnées (vainqueur)",
                "w_bpSaved": "BP sauvées (vainqueur)",
                "w_bpFaced": "BP subies (vainqueur)",

                "l_ace": "Aces (perdant)",
                "l_df": "Doubles fautes (perdant)",
                "l_1stIn": "1res IN (perdant)",
                "l_1stWon": "1res gagnées (perdant)",
                "l_bpSaved": "BP sauvées (perdant)",
                "l_bpFaced": "BP subies (perdant)",
            }

            # 1) Renommer d'abord
            matches_df = matches_df.rename(columns=FR_COLS)

            # 2) Supprimer la colonne technique
            matches_df = matches_df.drop(columns=["ID tournoi", "winner_id", "loser_id", "match_num"], errors="ignore")

            # 3) Date sans heure
            matches_df["Date"] = pd.to_datetime(matches_df["Date"], errors="coerce").dt.date

            # 4) Durée lisible
            def format_duration(minutes):
                if pd.isna(minutes) or minutes <= 0:
                    return "—"
                minutes = int(minutes)
                if minutes < 60:
                    return f"{minutes} min"
                h = minutes // 60
                m = minutes % 60
                return f"{h}h{m:02d}"

            matches_df["Durée"] = matches_df["Durée (min)"].apply(format_duration)
            matches_df = matches_df.drop(columns=["Durée (min)"], errors="ignore")

            gb = GridOptionsBuilder.from_dataframe(players_filtered)
            gb.configure_selection(selection_mode="single", use_checkbox=False)
            gb.configure_column("name", header_name="Joueur", sortable=True, filter=True, cellStyle={"fontWeight": "bold"})
            grid_options = gb.build()

            grid_response = AgGrid(
                players_filtered,
                gridOptions=grid_options,
                update_mode="SELECTION_CHANGED",
                fit_columns_on_grid_load=True,
                height=320
            )

            selected = grid_response.get("selected_rows", [])
            if isinstance(selected, pd.DataFrame) and not selected.empty:
                selected_row = selected.iloc[0]
                player_name = selected_row["name"]
                st.info(f"Joueur sélectionné : {player_name}")

                player_name_lower = player_name.lower().strip()

                player_matches = matches_df[
                    (matches_df["Vainqueur"].fillna("").str.lower().str.strip() == player_name_lower) |
                    (matches_df["Perdant"].fillna("").str.lower().str.strip() == player_name_lower)
                ]

                st.subheader(f"Matchs joués par {player_name}")
                st.dataframe(player_matches)
            else:
                st.info("Sélectionne un joueur pour afficher ses matchs.")

        except Exception as e:
            st.error(f"Erreur lors du chargement des joueurs : {e}")

    with tab2:
        st.header("Liste des matchs")
        try:
            matches_df = pd.read_sql("SELECT * FROM matches LIMIT 100", engine)
            st.dataframe(matches_df)
        except Exception as e:
            st.error(f"Erreur lors du chargement des matchs : {e}")

if __name__ == "__main__":
    display_stats()
