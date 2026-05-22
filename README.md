# Data Engineering & Analytics Portfolio

## Profil

Étudiant à **42 Paris**, avec un fort intérêt pour :

- la conception de **pipelines data**
- la **structuration et modélisation** des données
- l’**automatisation** des tâches

---

## Compétences clés

### Langages

- Python · SQL · Bash · R · C/C++

### Data Engineering & Architecture

- ETL / ELT
- Ingestion de données
- APIs
- Modélisation relationnelle
- Pipelines analytiques

### Bases de données & stockage

- PostgreSQL · BigQuery · DuckDB · SQLite · Parquet

### Cloud & DevOps

- GCP (BigQuery, GCS, Cloud Run, Pub/Sub)
- Docker · Docker Compose · CI/CD

### Machine Learning

- scikit-learn · TensorFlow · Keras · OpenAI Gym

### Visualisation & BI

- Streamlit · Matplotlib · Seaborn · Power BI · Excel

### Systèmes & collaboration

- Linux · Git (GitHub, GitLab) · automatisation Bash

---

## Projets mis en avant

### Crypto Market Pulse — Pipeline Data Temps Réel

<p align="center">
  <img src="crypto_market_pulse/assets/1.png" width="800"/><br/>
  <sub>Dashboard interactif — Prix et indicateurs techniques</sub>
</p>

<br/>

<p align="center">
  <img src="crypto_market_pulse/assets/2.png" width="800"/><br/>
  <sub>Suivi du sentiment de marché (Fear & Greed Index)</sub>
</p>

<br/>

<p align="center">
  <img src="crypto_market_pulse/assets/3.png" width="800"/><br/>
  <sub>Corrélations et indicateurs clés (RSI, volatilité)</sub>
</p>

Pipeline complet pour collecter, transformer et visualiser des **données crypto en quasi temps réel** — en cherchant à répondre à la question : le sentiment de marché prédit-il les mouvements de prix ?

- Collecte automatique toutes les heures des prix **BTC, ETH, BNB, SOL** (CoinGecko)
- Orchestration des tâches avec **Apache Airflow**
- Traitement et calcul d’indicateurs techniques (**RSI, volatilité**) avec **PySpark**
- Modélisation en couches **Bronze → Silver → Gold** avec **dbt**
- Stockage dans **PostgreSQL**, visualisation avec **Streamlit**
- Environnement entièrement **Dockerisé**

Dossier : `crypto_market_pulse/`

---

### GCP Weather Pulse — Pipeline Serverless Cloud

<p align="center">
  <img src="gcp_weather_pulse/assets/tableau_de_bord1.png" width="800"/><br/>
  <sub>Dashboard météo — Températures et précipitations</sub>
</p>

<br/>

<p align="center">
  <img src="gcp_weather_pulse/assets/tableau_de_bord2.png" width="800"/><br/>
  <sub>Analyse des tendances météo par ville</sub>
</p>

Pipeline cloud automatisé pour collecter, transformer et analyser des **données météo** — entièrement hébergé sur Google Cloud, sans serveur à gérer.

- Collecte automatique des données météo via **Cloud Run**
- Planification des exécutions avec **Cloud Scheduler**
- Stockage des données brutes dans **GCS (Bronze)**
- Transformation et chargement dans **BigQuery (Silver)**
- Vues analytiques prêtes à l’analyse (**Gold**)
- Architecture **serverless**, automatisée et reproductible

Dossier : `gcp_weather_pulse/`

---

### Game Price Predictor — Machine Learning

Modèle de Machine Learning pour **prédire le prix de vente de jeux vidéo** à partir de leurs caractéristiques (plateforme, genre, année de sortie, etc.).

- Préparation et nettoyage des données
- Modélisation avec **TensorFlow / Keras** (Deep Learning)
- Résultats : **R² = 0.90**, MAE = 4.70 €
- Évaluation des performances (MAE, RMSE, R²)

Dossier : `price_sale_prediction/`

---

### Product Sales Dashboard — Power BI

<p align="center">
  <img src="powerbi_product_dashboard/assets/dashboard_img.png" width="800"/><br/>
  <sub>Dashboard Power BI — Performance commerciale</sub>
</p>

Dashboard **Power BI** orienté pilotage de la performance commerciale, conçu comme un cas réaliste d’entreprise.

- Modélisation des données en **schéma en étoile**
- Indicateurs clés (**KPI, ratios, marges**) calculés avec **DAX**
- Analyse des tendances **semaine / mois / trimestre**
- Performance par vendeur, équipe et catégorie de produit
- Design orienté **lecture exécutive & décisionnelle**

Dossier : `powerbi_product_dashboard/`

---

## Autres projets

### Tennis Stats Tracker — Data Pipeline & Dashboard

<p align="center">
  <img src="tennis_stats_tracker/assets/photo2.png" width="800"/><br/>
  <sub>Table complète des matchs</sub>
</p>

<br/>

<p align="center">
  <img src="tennis_stats_tracker/assets/photo1.png" width="800"/><br/>
  <sub>Liste des joueurs</sub>
</p>

<br/>

<p align="center">
  <img src="tennis_stats_tracker/assets/photo3.png" width="800"/><br/>
  <sub>Matchs du joueur sélectionné</sub>
</p>

Pipeline ETL et application interactive pour l’analyse de **performances de tennis**.

- Collecte et nettoyage de données sportives (ATP)
- Modélisation relationnelle
- Stockage **PostgreSQL**
- Requêtes SQL analytiques
- Dashboard interactif avec **Streamlit**
- Environnement **Dockerisé**

Dossier : `tennis_stats_tracker/`

---

### Snake Agent RL — Reinforcement Learning Analysis

<p align="center">
  <img src="snake_agent_rl/assets/demo_snake.gif" width="500"/>
</p>

▶️ **Vidéo complète** : [`snake_agent_rl/assets/demo_snake.mp4`](snake_agent_rl/assets/demo_snake.mp4)

![Dashboard snake agent 1](snake_agent_rl/assets/photo1.png)
![Dashboard snake agent 2](snake_agent_rl/assets/photo2.png)
![Dashboard snake agent 3](snake_agent_rl/assets/photo3.png)

Analyse des données d’apprentissage d’un agent de **reinforcement learning**.

- Environnement personnalisé basé sur **OpenAI Gym**
- Collecte et analyse des métriques d’entraînement
- Étude de la convergence et de l’exploration/exploitation
- Visualisation et interprétation des performances

Dossier : `snake_rl_agent/`

---

### Mini Data Lake — Pollution de l’air

`mini_data_lake/`

- Nettoyage et transformation de données CSV
- Conversion en **Parquet optimisé**
- Interrogation avec **DuckDB**
- Analyse locale type Data Lake

---

### Food Nutrition Pipeline — ETL & API

`food_nutrition_pipeline/`

- Extraction de données via l’API **Open Food Facts**
- Orchestration ETL avec **Luigi**
- Transformation de données **XML**
- Stockage **Parquet + SQLite**
- Exposition des résultats via **API Flask**
- Déploiement **Docker**

---

### NPS Prediction — Data Analysis & ML

`nps_prediction/`

- Analyse de données clients
- Text mining
- Modélisation prédictive
- Visualisation avec **RMarkdown / Shiny**

---

## Ce que je mets concrètement en pratique

- Conception de **pipelines de données robustes**
- Modélisation et exploitation de bases de données
- Automatisation de traitements
- Environnements **Dockerisés**
- Utilisation d’outils **cloud** en conditions réelles

---

## Contact

- Email : **miguelfaucheux@hotmail.com**
- GitHub : https://github.com/Tee-Mig
- Profil 42 : https://cv.42.fr/fPu1xydA
