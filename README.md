# Data Engineering & Analytics Portfolio

## Profil

Étudiant à **42 Paris**, avec un fort intérêt pour :

- la conception de **pipelines data**
- la **structuration et modélisation** des données
- l’**automatisation** des tâches

---

## Compétences clés

### Langages

- Python · SQL · R · Bash · C/C++

### Data Engineering & Orchestration

- Apache Airflow · Luigi · dbt · PySpark
- ETL / ELT · Ingestion · APIs
- Modélisation relationnelle · Architecture Medallion (Bronze / Silver / Gold)

### Bases de données & stockage

- PostgreSQL · BigQuery · DuckDB · SQLite · Supabase · Parquet

### Cloud & DevOps

- GCP (BigQuery, GCS, Cloud Run, Pub/Sub, Cloud Scheduler)
- Docker · Docker Compose · CI/CD

### Machine Learning & Computer Vision

- scikit-learn · TensorFlow · Keras · OpenCV
- Reinforcement Learning (Q-Learning, DQN) · Gymnasium

### Visualisation & BI

- Streamlit · Flask · Power BI · Shiny · Matplotlib · Seaborn

### Systèmes & collaboration

- Linux · Git (GitHub, GitLab) · automatisation Bash

---

## Projets mis en avant

### Crypto Market Pulse - Pipeline Data Temps Réel

<p align="center">
  <img src="crypto_market_pulse/assets/1.png" width="800"/><br/>
  <sub>Dashboard interactif</sub>
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

Pipeline complet pour collecter, transformer et visualiser des **données crypto en quasi temps réel**, en cherchant à répondre à une question clé : le sentiment de marché prédit-il les mouvements de prix ?

- Collecte automatique toutes les heures des prix **BTC, ETH, BNB, SOL** (CoinGecko)
- Orchestration des tâches avec **Apache Airflow**
- Traitement et calcul d’indicateurs techniques (**RSI, volatilité**) avec **PySpark**
- Modélisation en couches **Bronze → Silver → Gold** avec **dbt**
- Stockage dans **PostgreSQL**, visualisation avec **Streamlit**
- Environnement entièrement **Dockerisé**

Dossier : `crypto_market_pulse/`

---

### GCP Weather Pulse - Pipeline Serverless Cloud

<p align="center">
  <img src="gcp_weather_pulse/assets/tableau_de_bord1.png" width="800"/><br/>
  <sub>Dashboard météo</sub>
</p>

<br/>

<p align="center">
  <img src="gcp_weather_pulse/assets/tableau_de_bord2.png" width="800"/><br/>
  <sub>Analyse des tendances météo par ville</sub>
</p>

Pipeline cloud automatisé pour collecter, transformer et analyser des **données météo**, entièrement hébergé sur Google Cloud, sans serveur à gérer.

- Collecte automatique des données météo via **Cloud Run**
- Planification des exécutions avec **Cloud Scheduler**
- Stockage des données brutes dans **GCS (Bronze)**
- Transformation et chargement dans **BigQuery (Silver)**
- Vues analytiques prêtes à l’analyse (**Gold**)
- Architecture **serverless**, automatisée et reproductible

Dossier : `gcp_weather_pulse/`

---

### Game Price Predictor - Machine Learning

<p align="center">
  <img src="price_sale_prediction/assets/UI.png" width="800"/><br/>
  <sub>Interface de prédiction</sub>
</p>

Modèle de Machine Learning pour **prédire le prix de vente de jeux vidéo** à partir de leurs caractéristiques (plateforme, genre, année de sortie, etc.).

- Préparation et nettoyage des données
- Modélisation avec **TensorFlow / Keras** (Deep Learning)
- Résultats : **R² = 0.90**, MAE = 4.70 €
- Évaluation des performances (MAE, RMSE, R²)

Dossier : `price_sale_prediction/`

---

### Product Sales Dashboard - Power BI

<p align="center">
  <img src="powerbi_product_dashboard/assets/dashboard_img.png" width="800"/><br/>
  <sub>Dashboard Power BI</sub>
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

### Anti-gaspi Shopify - Étude de Cas Data

Étude de cas technique réalisée en 2h pour un poste **Data / Tech** : transformer des données opérationnelles en décisions concrètes d’affichage produit sur Shopify.

- Analyse des données produit (stock, dates de péremption, ventes)
- Calcul d’un **score de priorité anti-gaspi** pour classer les produits
- Génération d’un payload **Shopify GraphQL** pour réordonner une collection
- Stockage des données avec **Supabase** et analyses via **BigQuery**
- Maquette d’un outil interne Ops / Marketing avec KPI et prévisualisation

Dossier : `cas_pratique_willy_anti_gaspi/`

---

### Tennis Stats Tracker - Data Pipeline & Dashboard

<p align="center">
  <img src="tennis_stats_tracker/assets/photo1.png" width="800"/><br/>
  <sub>Liste des joueurs</sub>
</p>

<br/>

<p align="center">
  <img src="tennis_stats_tracker/assets/photo2.png" width="800"/><br/>
  <sub>Table complète des matchs</sub>
</p>

<br/>

<p align="center">
  <img src="tennis_stats_tracker/assets/photo3.png" width="800"/><br/>
  <sub>Matchs du joueur sélectionné</sub>
</p>

Pipeline ETL et application interactive pour l’analyse de **statistiques de tennis ATP**.

- Collecte et nettoyage de données sportives (ATP)
- Modélisation relationnelle et stockage **PostgreSQL**
- Requêtes SQL analytiques
- Dashboard interactif avec **Streamlit**
- Environnement **Dockerisé**

Dossier : `tennis_stats_tracker/`

---

### Rune OCR Analyzer - Analyse d’Images par ML

<p align="center">
  <img src="rune_ocr_analyzer/assets/ui1.png" width="800"/><br/>
  <sub>Interface web</sub>
</p>

<br/>

<p align="center">
  <img src="rune_ocr_analyzer/assets/ui2.png" width="800"/><br/>
  <sub>Résultats d’analyse</sub>
</p>

<br/>

<table align="center">
  <tr>
    <td><img src="rune_ocr_analyzer/assets/analyse1.png" width="240"/></td>
    <td><img src="rune_ocr_analyzer/assets/analyse2.png" width="240"/></td>
    <td><img src="rune_ocr_analyzer/assets/analyse3.png" width="240"/></td>
  </tr>
  <tr>
    <td><img src="rune_ocr_analyzer/assets/analyse4.png" width="240"/></td>
    <td><img src="rune_ocr_analyzer/assets/analyse5.png" width="240"/></td>
    <td><img src="rune_ocr_analyzer/assets/analyse6.png" width="240"/></td>
  </tr>
  <tr>
    <td><img src="rune_ocr_analyzer/assets/analyse7.png" width="240"/></td>
    <td><img src="rune_ocr_analyzer/assets/analyse8.png" width="240"/></td>
    <td><img src="rune_ocr_analyzer/assets/analyse9.png" width="240"/></td>
  </tr>
  <tr>
    <td><img src="rune_ocr_analyzer/assets/analyse10.png" width="240"/></td>
    <td><img src="rune_ocr_analyzer/assets/analyse11.png" width="240"/></td>
    <td></td>
  </tr>
</table>

Application web pour **analyser automatiquement des images de runes** par OCR et règles métier.

- Reconnaissance de texte sur images avec **OCR**
- Calcul automatique d’équivalences et scores
- Interface web interactive avec **Flask**
- Journalisation et historique des analyses

Dossier : `rune_ocr_analyzer/`

---

### Food Nutrition Pipeline - ETL & API

Pipeline de données automatisé pour extraire et analyser des **informations nutritionnelles** de produits alimentaires.

- Extraction de données via l’API **Open Food Facts**
- Orchestration ETL avec **Luigi**
- Transformation de données XML et stockage **Parquet + SQLite**
- Exposition des résultats via une **API Flask**
- Déploiement **Docker**

Dossier : `food_nutrition_pipeline/`

---

### NPS Prediction - Machine Learning & Text Mining

Analyse des retours clients pour **prédire le Net Promoter Score** et identifier les leviers d’amélioration.

- Analyse de données clients quantitatives et textuelles
- **Text mining** et traitement du langage naturel
- Modélisation prédictive avec **Random Forest**
- Dashboard interactif avec **Shiny** (R)

Dossier : `nps_prediction/`

---

### RL Agents - Reinforcement Learning

Plusieurs agents de **reinforcement learning** appliqués à des environnements classiques, jusqu’à un agent DQN jouant à Snake en temps réel.

- **Q-Learning** sur CartPole, FrozenLake, MountainCar (Gymnasium)
- Agent **DQN** avec réseau convolutionnel (CNN) inspiré de DeepMind Atari
- Capture d’écran en temps réel + **OCR** pour lire le score
- Suivi des métriques d’entraînement avec **Pandas / Matplotlib**

Dossier : `rl_agents/`

---

### Snake Agent RL - Analyse de Données d'Entraînement

<p align="center">
  <img src="snake_agent_rl/assets/demo_snake.gif" width="500"/><br/>
  <sub>Agent en action</sub>
</p>

<br/>

<p align="center">
  <img src="snake_agent_rl/assets/photo1.png" width="800"/><br/>
  <sub>Métriques d'entraînement</sub>
</p>

<br/>

<p align="center">
  <img src="snake_agent_rl/assets/photo2.png" width="800"/><br/>
  <sub>Courbe de convergence</sub>
</p>

<br/>

<p align="center">
  <img src="snake_agent_rl/assets/photo3.png" width="800"/><br/>
  <sub>Analyse exploration / exploitation</sub>
</p>

Analyse des données d'apprentissage d'un **agent Snake entraîné par reinforcement learning**.

- Environnement personnalisé basé sur **OpenAI Gym**
- Collecte et analyse des **métriques d'entraînement**
- Étude de la **convergence** et du compromis exploration / exploitation
- Visualisation et interprétation des performances de l'agent

Dossier : `snake_agent_rl/`

---

### Comparateur de Prix - Agrégation Multi-Sources

Outil pour **comparer des prix produits** en agrégeant plusieurs sources de données hétérogènes.

- Interrogation de 3 sources distinctes : **API REST JSON**, **XML**, **SerpAPI**
- Normalisation multi-format (JSON, XML) en un DataFrame unifié avec **Pandas**
- Export des résultats en **CSV** et base **SQLite**
- Visualisation de la distribution des prix avec **Matplotlib**

Dossier : `comparateur_prix/`

---

### Mini Data Lake - Pollution de l’air

Démonstration d’une architecture **Data Lake** pour analyser des données de pollution atmosphérique.

- Nettoyage et transformation de données CSV
- Conversion en **Parquet optimisé**
- Interrogation locale et distante avec **DuckDB**
- Visualisation avec **Matplotlib**

Dossier : `mini_data_lake/`

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
