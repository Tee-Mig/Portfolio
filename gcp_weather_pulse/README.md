# Weather Pulse — Serverless Data Pipeline (GCP)

Pipeline **100% serverless** qui ingère des données météo (Open-Meteo), stocke le **brut** en **GCS (bronze)**, transforme en **BigQuery (silver)**, expose des **vues analytiques (gold)** et s’exécute automatiquement via **Cloud Scheduler**.  
Optionnel : un **dashboard Streamlit** sur Cloud Run.

---

## Stack

- **Ingestion (Étape 1)** : Cloud Run `weather-fetcher` → GCS `gs://$RAW_BUCKET/raw/YYYY/MM/DD/HH/payload.json`
- **Transport (Étape 2)** : Pub/Sub (push **OIDC**)
- **Transform (Étape 2)** : Cloud Run `weather-transformer` → BigQuery `weather.observations` (partitionné par `DATE(ts)`)
- **Serving (Étape 2.5)** : BigQuery Views `weather.v_hourly_city` (propre), `weather.v_daily_city` (agrégé)
- **Orchestration (Étape 3)** : Cloud Scheduler → POST OIDC `/run`
- **Dashboard (option)** : Streamlit `weather-dashboard` (Cloud Run)

**OS/CLI** : Windows + Git Bash + Google Cloud SDK (gcloud/gsutil/bq)

---

## Variables d’environnement

Créer un fichier **`.env`** à la racine :

```bash
PROJECT_ID=my-data-xxxx
REGION=europe-west1
RAW_BUCKET=weather-raw-my-data-xxxx
```

## Charger l’env dans Bash

make env-shell # ouvre un shell interactif avec .env chargé
make print-env # vérifie les valeurs

## Architecture

Cloud Scheduler (OIDC)
│ POST /run (cron)
▼
Cloud Run weather-fetcher
│ écrit JSON brut
▼
GCS (bronze) gs://$RAW_BUCKET/raw/YYYY/MM/DD/HH/payload.json
│ publie path (attributes)
▼
Pub/Sub (topic: weather-transform, push OIDC)
│ POST /process (OIDC)
▼
Cloud Run weather-transformer
│ insert
▼
BigQuery (silver) weather.observations (PARTITION BY DATE(ts))
│
├─ View (gold) weather.v_hourly_city → 1 ville × 1 heure
└─ View (gold) weather.v_daily_city → moyennes / totaux par jour

## Déploiement

## Étape 1 — Ingestion → GCS (bronze)

make init # set project + APIs Storage/Run/Build
make bucket # crée le bucket RAW si absent
make build_fetcher
make deploy_fetcher
make run_once # déclenche 1 ingestion
make peek # affiche le dernier payload.json (sanity check)
make logs_fetcher # logs du fetcher

## Étape 2 — Transform → BigQuery (silver) via Pub/Sub OIDC

make enable_step2_apis
make bq_dataset
make bq_table
make build_transformer
make deploy_transformer
make pubsub_bind # topic + subscription push OIDC + roles/run.invoker
make grant_pubsub_publish # fetcher -> roles/pubsub.publisher
make redeploy_fetcher_pubsub # injecte PUBSUB_TOPIC dans le fetcher
make run_once
make logs_transformer # doit voir POST /process 200
make demo_query # compte les lignes récentes
make demo_sample # échantillon (ville, ts, temp)

## Étape 2.5 — Vues (gold)

make gold_views
make demo_view_hourly
make demo_view_daily

## Dashboard — Streamlit sur Cloud Run

make build_dashboard
make deploy_dashboard
make dashboard_url
