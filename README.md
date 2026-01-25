# Projets & Portfolio

Bienvenue sur ce dépôt qui regroupe mes **projets académiques et personnels** réalisés dans le cadre de ma formation à **42 Paris**, ainsi que des projets liés aux données, aux bases de données, à l’automatisation et au backend.

Ce dépôt Github sert de point d’entrée pour découvrir mon travail, mon approche technique et les technologies que j’utilise au quotidien.


## À propos de moi

Je suis étudiant à **42 Paris**, avec un intérêt marqué pour l’informatique appliquée, les bases de données et le traitement de données.

J’apprécie particulièrement :
- concevoir des projets complets et cohérents,
- structurer et exploiter des données,
- **automatiser** des traitements et des flux,
- rendre des solutions techniques compréhensibles et réutilisables


## Technologies & outils

### Langages
- Python
- SQL
- R
- C / C++

### Bases de données & stockage
- PostgreSQL
- DuckDB
- SQLite
- BigQuery
- Parquet

### Cloud & services managés
- Google Cloud Platform
- Google Cloud Storage
- Cloud Run
- Cloud Scheduler
- Pub/Sub
- BigQuery

### Pipelines & automatisation
- Pipelines ETL / ELT
- Orchestration de workflows (Luigi)
- Scripts Python d’ingestion et de transformation
- Automatisation via Makefile
- Nettoyage, normalisation et préparation des données

### Infrastructure & environnement
- Docker
- Docker Compose

### Librairies & outils data
- pandas
- pyarrow
- lxml
- sqlalchemy
- matplotlib

### Visualisation & restitution
- Streamlit
- Shiny (R)

### 🔧 Outils système & collaboration
- Git / GitHub
- Linux
- Bash


## Projets mis en avant

### Weather Pulse — Serverless Data Pipeline (GCP)
`gcp-weather-pulse/`

Pipeline de données serverless pour l’ingestion, la transformation et l’exposition analytique de données météo.

- Ingestion automatisée via Cloud Run et Cloud Scheduler
- Stockage des données brutes en GCS (bronze)
- Transformation et chargement dans BigQuery (silver)
- Exposition de vues analytiques (gold)
- Architecture orientée automatisation et reproductibilité


### Mini Data Lake — Analyse de la pollution de l’air
`mini_data_lake/`

Implémentation d’un **mini Data Lake local** basé sur des fichiers Parquet interrogeables via SQL.

- Nettoyage et transformation de données CSV
- Conversion en Parquet optimisé
- Interrogation locale et distante avec DuckDB
- Visualisation des données


### Food Nutrition Pipeline
`food_nutrition_pipeline/`

Pipeline ETL automatisé pour l’extraction et l’analyse de données nutritionnelles issues de l’API Open Food Facts.

- Orchestration des tâches ETL avec Luigi
- Transformation de données XML
- Stockage optimisé (Parquet + SQLite)
- Exposition des résultats via une API Flask
- Déploiement et exécution via Docker


### Tennis Stats Tracker
`tennis_stats_tracker/`

Pipeline ETL et application de visualisation de statistiques de tennis.

- Nettoyage et transformation de données ATP
- Modélisation relationnelle et stockage PostgreSQL
- Requêtes SQL analytiques
- Interface Streamlit interactive
- Environnement conteneurisé avec Docker


### NPS Prediction
`nps_prediction/`

Projet d’analyse et de prédiction du **Net Promoter Score** à partir de données clients structurées et textuelles.

- Préparation et exploration des données
- Analyse de texte (text mining)
- Entraînement de modèles de machine learning
- Visualisation et restitution des résultats (RMarkdown / Shiny)



### Game Price / Sales Prediction
`price_sale_prediction/`

Projet de prédiction du prix de vente de jeux vidéo à partir de données structurées.

- Préparation et transformation des données
- Feature engineering
- Modélisation avec TensorFlow / Keras
- Évaluation des performances du modèle


## Ce que je mets en pratique

- Conception et exploitation de bases de données
- Construction de pipelines de données
- Automatisation de traitements
- Utilisation d’outils cloud et conteneurisation


## Contact

- Email : **miguelfaucheux@hotmail.com**
- GitHub : https://github.com/Tee-Mig
- Profil 42 : https://cv.42.fr/fPu1xydA


Merci de votre visite. N’hésitez pas à explorer les projets ou à me contacter.
