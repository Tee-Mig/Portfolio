.PHONY: help setup up down restart rebuild ps logs logs-airflow logs-spark logs-dashboard init dbt-run dbt-test clean urls

help:
	@echo "Crypto Market Pulse — commandes disponibles"
	@echo ""
	@echo "  make setup           → .env + télécharge le JDBC jar"
	@echo "  make init            → initialise la base Airflow (à lancer une seule fois)"
	@echo "  make up              → démarre tous les conteneurs"
	@echo "  make down            → arrête et supprime les conteneurs"
	@echo "  make restart         → down + up"
	@echo "  make rebuild         → rebuild les images + up"
	@echo "  make ps              → état des conteneurs"
	@echo "  make logs            → suit tous les logs en temps réel"
	@echo "  make logs-airflow    → logs du scheduler Airflow"
	@echo "  make logs-spark      → logs du master Spark"
	@echo "  make logs-dashboard  → logs du dashboard Streamlit"
	@echo "  make dbt-run         → exécute tous les modèles dbt"
	@echo "  make dbt-test        → lance les tests dbt"
	@echo "  make clean           → down + suppression des volumes (reset complet)"
	@echo "  make urls            → affiche les URLs des services"

setup:
	@if [ ! -f .env ]; then cp .env.example .env; echo ".env créé — remplis REDDIT_CLIENT_ID et AIRFLOW_FERNET_KEY"; fi
	@bash scripts/download-jars.sh
	@mkdir -p data/bronze/prices data/bronze/reddit airflow/logs

init:
	docker compose run --rm airflow-init

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose down && docker compose up -d

rebuild:
	docker compose down && docker compose up --build -d

ps:
	docker compose ps

logs:
	docker compose logs -f

logs-airflow:
	docker compose logs -f airflow-scheduler

logs-spark:
	docker compose logs -f spark-master

logs-dashboard:
	docker compose logs -f dashboard

dbt-run:
	docker compose exec airflow-scheduler bash -c "cd /opt/dbt && dbt run --profiles-dir ."

dbt-test:
	docker compose exec airflow-scheduler bash -c "cd /opt/dbt && dbt test --profiles-dir ."

clean:
	docker compose down -v

urls:
	@echo "Airflow UI   → http://localhost:8080  (admin / admin)"
	@echo "Spark UI     → http://localhost:8082"
	@echo "Dashboard    → http://localhost:8501"
	@echo "PostgreSQL   → localhost:5432  db: crypto_pulse"
