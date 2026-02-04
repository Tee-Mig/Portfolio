# =======================================
#  Weather Pulse - Makefile (Windows Git Bash friendly)
# =======================================
SHELL := /usr/bin/bash
.ONESHELL:

# -------- Help --------
.PHONY: help
help:
	@echo "Weather Pulse - Make targets"
	@echo ""
	@echo "[Env]"
	@echo "  make check-env             # verify PROJECT_ID, REGION, RAW_BUCKET"
	@echo "  make env-shell             # open a subshell with .env loaded"
	@echo "  make print-env             # print current env"
	@echo ""
	@echo "[Step 1 - Ingestion -> GCS]"
	@echo "  make init                  # set project + enable core APIs"
	@echo "  make bucket                # create RAW bucket if missing"
	@echo "  make build_fetcher         # build fetcher image (Cloud Build)"
	@echo "  make deploy_fetcher        # deploy fetcher on Cloud Run (public)"
	@echo "  make fetcher_url           # print fetcher URL"
	@echo "  make run_once              # trigger one ingestion (POST /run)"
	@echo "  make logs_fetcher          # tail fetcher logs"
	@echo "  make check-payload         # list latest raw payload(s) in GCS"
	@echo "  make peek                  # pretty print last payload.json"
	@echo "  make peek-cities           # items count + first cities from last payload"
	@echo "  make grant_gcs_role        # grant bucket role to fetcher SA if 403"
	@echo "  make destroy               # delete fetcher + RAW bucket"
	@echo ""
	@echo "[Step 2 - Transform -> BigQuery (Pub/Sub -> Cloud Run)]"
	@echo "  make enable_step2_apis     # enable BigQuery + Pub/Sub APIs"
	@echo "  make bq_dataset            # create dataset 'weather' (EU)"
	@echo "  make bq_table              # create table weather.observations"
	@echo "  make build_transformer     # build transformer image"
	@echo "  make deploy_transformer    # deploy transformer (private)"
	@echo "  make test_transformer      # /process once with last GCS path"
	@echo "  make pubsub_bind           # topic/sub push OIDC -> transformer"
	@echo "  make grant_pubsub_publish  # allow fetcher to publish"
	@echo "  make redeploy_fetcher_pubsub # redeploy fetcher with PUBSUB_TOPIC"
	@echo "  make logs_transformer      # tail transformer logs"
	@echo "  make demo_query            # count rows last 2 days"
	@echo "  make demo_query_save       # save count JSON to results/"
	@echo "  make demo_sample           # sample 10 rows from v_hourly_city"
	@echo "  make step2_down            # delete transformer + topic + sub"
	@echo ""
	@echo "[Step 2.5 - Gold Views]"
	@echo "  make gold_views            # create v_hourly_city, v_daily_city"
	@echo "  make demo_view_hourly      # sample latest rows from v_hourly_city"
	@echo "  make demo_view_daily       # sample latest rows from v_daily_city"
	@echo "  make gold_down             # drop gold views"
	@echo ""
	@echo "[Step 3 - Orchestration (Scheduler -> /run)]"
	@echo "  make enable_step3_apis     # enable Cloud Scheduler API"
	@echo "  make scheduler_sa_up       # create scheduler SA + grant run.invoker"
	@echo "  make scheduler_up          # create/update cron job"
	@echo "  make scheduler_run_now     # run job immediately"
	@echo "  make scheduler_info        # show job status/details"
	@echo "  make scheduler_down        # delete scheduler job"
	@echo "  make fetcher_private       # make fetcher private (OIDC only)"
	@echo "  make run_once_auth         # POST /run with identity token"
	@echo ""
	@echo "[Dashboard (Streamlit)]"
	@echo "  make build_dashboard       # build dashboard image"
	@echo "  make deploy_dashboard      # deploy dashboard (public)"
	@echo "  make dashboard_url         # print dashboard URL"
	@echo "  make dash_venv             # create venv + install deps locally"
	@echo "  make dash_local            # run Streamlit locally on :8080"
	@echo "  make dash_open             # open http://localhost:8080"
	@echo "  make dash_local_docker     # run dashboard via Docker (mount gcloud creds)"
	@echo ""
	@echo "[Teardown]"
	@echo "  make stop_scheduler        # pause scheduler"
	@echo "  make services_down         # delete Run services"
	@echo "  make silver_down           # drop table weather.observations"
	@echo "  make dataset_down          # drop dataset weather"
	@echo "  make bronze_down           # delete RAW bucket"
	@echo "  make sa_down               # delete helper service accounts"
	@echo "  make step3_down            # delete scheduler job"
	@echo "  make down_all              # full teardown"
	@echo "  make stop_all              # pause orchestration only"

# ===== Step 1: Ingestion -> GCS =====
.PHONY: check-env
check-env:
	@if [ -z "$$PROJECT_ID" ] || [ -z "$$REGION" ] || [ -z "$$RAW_BUCKET" ]; then \
		echo "[ERROR] Missing vars. Load .env with 'make env-shell' or export them."; \
		echo "Required: PROJECT_ID, REGION, RAW_BUCKET"; \
		exit 1; \
	else \
		echo "[OK] PROJECT_ID=$$PROJECT_ID REGION=$$REGION RAW_BUCKET=$$RAW_BUCKET"; \
	fi

.PHONY: env-shell
env-shell:
	if [ ! -f .env ]; then echo ".env not found" >&2; exit 1; fi
	echo "Opening shell with .env (type 'exit' to quit)..."
	set -a; . ./.env; set +a
	exec bash -i

.PHONY: print-env
print-env: check-env
	@echo "PROJECT_ID=$$PROJECT_ID"; echo "REGION=$$REGION"; echo "RAW_BUCKET=gs://$$RAW_BUCKET"

.PHONY: init
init: check-env
	gcloud config set project "$$PROJECT_ID"
	gcloud services enable run.googleapis.com cloudbuild.googleapis.com storage.googleapis.com containerregistry.googleapis.com

.PHONY: bucket
bucket: check-env
	@echo "Ensure bucket: gs://$$RAW_BUCKET"
	@gsutil ls -b "gs://$$RAW_BUCKET" >/dev/null 2>&1 || gsutil mb -p "$$PROJECT_ID" -l "$$REGION" "gs://$$RAW_BUCKET"
	@gsutil ls -b "gs://$$RAW_BUCKET"

.PHONY: build_fetcher
build_fetcher: check-env
	gcloud builds submit fetcher --tag gcr.io/$$PROJECT_ID/fetcher

.PHONY: deploy_fetcher
deploy_fetcher: check-env
	gcloud run deploy weather-fetcher \
	  --image gcr.io/$$PROJECT_ID/fetcher \
	  --region "$$REGION" \
	  --allow-unauthenticated \
	  --set-env-vars RAW_BUCKET=$$RAW_BUCKET

.PHONY: fetcher_url
fetcher_url: check-env
	@echo -n "weather-fetcher URL: "
	@gcloud run services describe weather-fetcher --region "$$REGION" --format='value(status.url)'

.PHONY: run_once
run_once: check-env
	@URL=$$(gcloud run services describe weather-fetcher --region "$$REGION" --format='value(status.url)'); \
	if [ -z "$$URL" ]; then echo "[ERROR] deploy fetcher first"; exit 1; fi; \
	powershell -NoProfile -Command "Invoke-WebRequest -UseBasicParsing -Method POST -Uri '$$URL/run' | Out-Null; Write-Output '[OK] Ingestion triggered'"

.PHONY: logs_fetcher
logs_fetcher: check-env
	gcloud run services logs read weather-fetcher --region "$$REGION" --limit 100

.PHONY: check-payload
check-payload: check-env
	gsutil ls -r "gs://$$RAW_BUCKET/raw/**/payload.json"

.PHONY: peek
peek: check-env
	@LAST=$$(gsutil ls -r "gs://$$RAW_BUCKET/raw/**/payload.json" | tail -n 1); echo "[peek] $$LAST"; gsutil cat "$$LAST" | python -m json.tool | less

.PHONY: peek-cities
peek-cities: check-env
	@echo "[env] RAW_BUCKET=$$RAW_BUCKET"
	@LAST=$$(gsutil ls -r "gs://$$RAW_BUCKET/raw/**/payload.json" | tail -n 1); \
	if [ -z "$$LAST" ]; then echo "[peek-cities] no payload"; exit 1; fi; \
	echo "[peek-cities] $$LAST"; \
	if ! gsutil cat "$$LAST" > .peek.json 2>/dev/null; then echo "[peek-cities] gsutil cat failed"; exit 1; fi; \
	python -c "import json; d=json.load(open('.peek.json','rb')); print('items:', len(d)); print('cities:', [x.get('city') for x in d][:10])"; \
	rm -f .peek.json

.PHONY: grant_gcs_role
grant_gcs_role: check-env
	@SA=$$(gcloud run services describe weather-fetcher --region "$$REGION" --format='value(spec.template.spec.serviceAccountName)'); \
	[ -n "$$SA" ] || { echo "[ERROR] service not deployed"; exit 1; }; \
	echo "Grant roles/storage.objectAdmin to $$SA on gs://$$RAW_BUCKET"; \
	gsutil iam ch serviceAccount:$$SA:roles/storage.objectAdmin "gs://$$RAW_BUCKET"

.PHONY: destroy
destroy: check-env
	- gcloud run services delete weather-fetcher --region "$$REGION" -q
	- gsutil -m rm -r "gs://$$RAW_BUCKET" || true
	@echo "[OK] Step 1 cleaned."

# ===== Step 2: Transform -> BigQuery =====
.PHONY: enable_step2_apis
enable_step2_apis: check-env
	gcloud services enable bigquery.googleapis.com pubsub.googleapis.com

.PHONY: bq_dataset
bq_dataset: check-env
	@echo "[bq_dataset] project=$$PROJECT_ID location=EU"
	CLOUDSDK_CORE_DISABLE_PROMPTS=1 bq --project_id="$$PROJECT_ID" --location=EU mk -d --description "Weather curated dataset" weather || true
	CLOUDSDK_CORE_DISABLE_PROMPTS=1 bq --project_id="$$PROJECT_ID" --location=EU ls --datasets | grep -E '(^|[[:space:]])weather($|[[:space:]])' >/dev/null 2>&1 && echo "[OK] dataset present" || (echo "[ERROR] dataset missing"; exit 1)

.PHONY: bq_table
bq_table: check-env
	@echo "[bq_table] $$PROJECT_ID.weather.observations"
	CLOUDSDK_CORE_DISABLE_PROMPTS=1 bq --project_id="$$PROJECT_ID" --location=EU mk --table \
	  --time_partitioning_field=ts \
	  "$$PROJECT_ID:weather.observations" \
	  city:STRING,ts:TIMESTAMP,temperature_2m:FLOAT,relative_humidity_2m:FLOAT,precipitation:FLOAT,wind_speed_10m:FLOAT || true
	CLOUDSDK_CORE_DISABLE_PROMPTS=1 bq --project_id="$$PROJECT_ID" --location=EU show "$$PROJECT_ID:weather.observations" >/dev/null && echo "[OK] table ready" || (echo "[ERROR] table missing"; exit 1)

.PHONY: build_transformer
build_transformer: check-env
	gcloud builds submit transformer --tag gcr.io/$$PROJECT_ID/transformer

.PHONY: deploy_transformer
deploy_transformer: check-env
	gcloud run deploy weather-transformer \
	  --image gcr.io/$$PROJECT_ID/transformer \
	  --region "$$REGION" \
	  --no-allow-unauthenticated \
	  --set-env-vars PROJECT_ID=$$PROJECT_ID,BQ_DATASET=weather,BQ_TABLE=observations,RAW_BUCKET=$$RAW_BUCKET

.PHONY: test_transformer
test_transformer: check-env
	@URL=$$(gcloud run services describe weather-transformer --region "$$REGION" --format='value(status.url)'); \
	[ -n "$$URL" ] || { echo "[ERROR] transformer not deployed"; exit 1; }; \
	LAST=$$(gsutil ls -r "gs://$$RAW_BUCKET/raw/**/payload.json" | tail -n 1); \
	[ -n "$$LAST" ] || { echo "[ERROR] no payload found"; exit 1; }; \
	PATH_IN_BUCKET=$${LAST#gs://$$RAW_BUCKET/}; \
	echo "[test_transformer] POST $$URL/process path=$$PATH_IN_BUCKET"; \
	curl -s -X POST "$$URL/process" -H "Content-Type: application/json" -d '{"message":{"attributes":{"path":"'"'"'$$PATH_IN_BUCKET'"'"'}}}' | sed 's/^/[resp] /'

.PHONY: pubsub_bind
pubsub_bind: check-env
	@URL=$$(gcloud run services describe weather-transformer --region "$$REGION" --format='value(status.url)'); \
	[ -n "$$URL" ] || { echo "[ERROR] transformer not deployed"; exit 1; }; \
	SA_EMAIL="pubsub-pusher@$$PROJECT_ID.iam.gserviceaccount.com"; \
	gcloud pubsub topics create weather-transform >/dev/null 2>&1 || true; \
	gcloud iam service-accounts describe $$SA_EMAIL >/dev/null 2>&1 || gcloud iam service-accounts create pubsub-pusher --display-name="Pub/Sub push SA"; \
	gcloud run services add-iam-policy-binding weather-transformer --region "$$REGION" --member="serviceAccount:$$SA_EMAIL" --role="roles/run.invoker" >/dev/null; \
	gcloud pubsub subscriptions delete weather-transform-sub -q >/dev/null 2>&1 || true; \
	gcloud pubsub subscriptions create weather-transform-sub --topic=weather-transform --push-endpoint="$$URL/process" --push-auth-service-account="$$SA_EMAIL"; \
	echo "[OK] Pub/Sub wired (OIDC)."

.PHONY: grant_pubsub_publish
grant_pubsub_publish: check-env
	@SA=$$(gcloud run services describe weather-fetcher --region "$$REGION" --format='value(spec.template.spec.serviceAccountName)'); \
	[ -n "$$SA" ] || { echo "[ERROR] fetcher not deployed"; exit 1; }; \
	gcloud projects add-iam-policy-binding "$$PROJECT_ID" --member="serviceAccount:$$SA" --role="roles/pubsub.publisher"

.PHONY: redeploy_fetcher_pubsub
redeploy_fetcher_pubsub: check-env
	gcloud run deploy weather-fetcher \
	  --image gcr.io/$$PROJECT_ID/fetcher \
	  --region "$$REGION" \
	  --allow-unauthenticated \
	  --set-env-vars RAW_BUCKET=$$RAW_BUCKET,PUBSUB_TOPIC=projects/$$PROJECT_ID/topics/weather-transform

.PHONY: logs_transformer
logs_transformer: check-env
	gcloud run services logs read weather-transformer --region "$$REGION" --limit 100

.PHONY: demo_query
demo_query: check-env
	@TOKEN=$$(gcloud auth print-access-token); \
	printf 'SELECT COUNT(*) AS n FROM `%s.weather.observations` WHERE DATE(ts) >= DATE_SUB(CURRENT_DATE(), INTERVAL 2 DAY)\n' "$$PROJECT_ID" > .query.sql; \
	python -c "import json,io; q=io.open('.query.sql','r',encoding='utf-8').read(); io.open('.body.json','w',encoding='utf-8').write(json.dumps({'query': q, 'useLegacySql': False}))"; \
	curl -s -X POST -H "Authorization: Bearer $$TOKEN" -H "Content-Type: application/json" -d @.body.json "https://bigquery.googleapis.com/bigquery/v2/projects/$$PROJECT_ID/queries" > .resp.json; \
	python -c "import json,io,sys; r=json.load(io.open('.resp.json','rb')); print('rows:', r.get('rows',[{'f':[{'v':0}]}])[0]['f'][0]['v']) if 'rows' in r else (print(r),sys.exit(1))"; \
	rm -f .query.sql .body.json .resp.json

.PHONY: demo_query_save
demo_query_save: check-env
	@mkdir -p results
	@TOKEN=$$(gcloud auth print-access-token); \
	printf 'SELECT COUNT(*) AS n FROM `%s.weather.observations` WHERE DATE(ts) >= DATE_SUB(CURRENT_DATE(), INTERVAL 2 DAY)\n' "$$PROJECT_ID" > results.query.sql; \
	python -c "import json,io; q=io.open('results.query.sql','r',encoding='utf-8').read(); io.open('results.body.json','w',encoding='utf-8').write(json.dumps({'query': q, 'useLegacySql': False}))"; \
	curl -s -X POST -H "Authorization: Bearer $$TOKEN" -H "Content-Type: application/json" -d @results.body.json "https://bigquery.googleapis.com/bigquery/v2/projects/$$PROJECT_ID/queries" > results/observations_count.json; \
	python -c "import json; r=json.load(open('results/observations_count.json','rb')); print('rows:', r['rows'][0]['f'][0]['v']) if 'rows' in r else print(r)"; \
	echo "Saved: results/observations_count.json"

.PHONY: demo_sample
demo_sample: check-env
	@TOKEN=$$(gcloud auth print-access-token); \
	: > .query.sql; \
	printf '%s\n' 'SELECT' >> .query.sql; \
	printf '%s\n' '  city,' >> .query.sql; \
	printf '%s\n' "  FORMAT_TIMESTAMP('%F %T', ts, 'Europe/Paris') AS ts_paris," >> .query.sql; \
	printf '%s\n' '  ROUND(temperature_2m,1) AS temperature_2m' >> .query.sql; \
	printf '%s\n' "FROM \`$${PROJECT_ID}.weather.v_hourly_city\`" >> .query.sql; \
	printf '%s\n' 'ORDER BY ts DESC' >> .query.sql; \
	printf '%s\n' 'LIMIT 10' >> .query.sql; \
	python -c "import json,io; q=io.open('.query.sql','r',encoding='utf-8').read(); io.open('.body.json','w',encoding='utf-8').write(json.dumps({'query': q, 'useLegacySql': False}))"; \
	curl -s -X POST -H "Authorization: Bearer $$TOKEN" -H "Content-Type: application/json" -d @.body.json "https://bigquery.googleapis.com/bigquery/v2/projects/$$PROJECT_ID/queries" > .resp.json; \
	python -c "import json,io,sys; r=json.load(io.open('.resp.json','rb')); print('\n'.join([f\"{row['f'][0]['v']}\t{row['f'][1]['v']}\t{row['f'][2]['v']}\" for row in r.get('rows',[])])) if 'rows' in r else (print(r),sys.exit(1))"; \
	rm -f .query.sql .body.json .resp.json

.PHONY: step2_down
step2_down: check-env
	- gcloud pubsub subscriptions delete weather-transform-sub -q || true
	- gcloud pubsub topics delete weather-transform -q || true
	- gcloud run services delete weather-transformer --region "$$REGION" -q || true
	@echo "[OK] Step 2 removed."

# ===== Gold Views =====
.PHONY: gold_hourly_view
gold_hourly_view: check-env
	@echo "[SQL] CREATE OR REPLACE VIEW weather.v_hourly_city"
	CLOUDSDK_CORE_DISABLE_PROMPTS=1 bq --project_id="$$PROJECT_ID" --location=EU query --use_legacy_sql=false \
	  "CREATE OR REPLACE VIEW \`$$PROJECT_ID.weather.v_hourly_city\` AS
	   SELECT city, ts, temperature_2m, relative_humidity_2m, precipitation, wind_speed_10m
	   FROM \`$$PROJECT_ID.weather.observations\`;"
	@echo "[OK] v_hourly_city created"

.PHONY: gold_daily_view
gold_daily_view: check-env
	@echo "[SQL] CREATE OR REPLACE VIEW weather.v_daily_city"
	CLOUDSDK_CORE_DISABLE_PROMPTS=1 bq --project_id="$$PROJECT_ID" --location=EU query --use_legacy_sql=false \
	  "CREATE OR REPLACE VIEW \`$$PROJECT_ID.weather.v_daily_city\` AS
	   SELECT
	     city,
	     DATE(ts) AS day,
	     AVG(temperature_2m)       AS avg_temp,
	     AVG(relative_humidity_2m) AS avg_humidity,
	     SUM(precipitation)        AS total_precip,
	     AVG(wind_speed_10m)       AS avg_wind
	   FROM \`$$PROJECT_ID.weather.v_hourly_city\`
	   GROUP BY city, day;"
	@echo "[OK] v_daily_city created"

.PHONY: gold_views
gold_views: check-env gold_hourly_view gold_daily_view
	@echo "[OK] Gold views ready: weather.v_hourly_city, weather.v_daily_city"

.PHONY: demo_view_hourly
demo_view_hourly: check-env
	CLOUDSDK_CORE_DISABLE_PROMPTS=1 bq --project_id="$$PROJECT_ID" --location=EU query --use_legacy_sql=false --format=csv \
	  "SELECT city, ts, temperature_2m FROM \`$$PROJECT_ID.weather.v_hourly_city\` ORDER BY ts DESC LIMIT 10"

.PHONY: demo_view_daily
demo_view_daily: check-env
	CLOUDSDK_CORE_DISABLE_PROMPTS=1 bq --project_id="$$PROJECT_ID" --location=EU query --use_legacy_sql=false --format=csv \
	  "SELECT city, day, avg_temp, total_precip, avg_wind FROM \`$$PROJECT_ID.weather.v_daily_city\` ORDER BY day DESC, city LIMIT 10"

.PHONY: gold_down
gold_down: check-env
	- bq rm -f -t "$$PROJECT_ID:weather.v_hourly_city" || true
	- bq rm -f -t "$$PROJECT_ID:weather.v_daily_city"  || true
	@echo "[OK] Gold views removed."

# ===== Step 3: Orchestration (Scheduler) =====
SCHED_CRON ?= 0 * * * *     # every hour
SCHED_JOB  ?= fetch-hourly-weather
SCHED_SA   ?= scheduler-caller

.PHONY: enable_step3_apis
enable_step3_apis: check-env
	@gcloud services enable cloudscheduler.googleapis.com

.PHONY: scheduler_sa_up
scheduler_sa_up: check-env
	@SA_EMAIL="$(SCHED_SA)@$$PROJECT_ID.iam.gserviceaccount.com"; \
	gcloud iam service-accounts describe $$SA_EMAIL >/dev/null 2>&1 || gcloud iam service-accounts create "$(SCHED_SA)" --display-name="Cloud Scheduler caller"; \
	gcloud run services add-iam-policy-binding weather-fetcher --region "$$REGION" --member="serviceAccount:$$SA_EMAIL" --role="roles/run.invoker" >/dev/null; \
	echo "[OK] Scheduler SA: $$SA_EMAIL"

.PHONY: scheduler_up
scheduler_up: check-env scheduler_sa_up
	@URL=$$(gcloud run services describe weather-fetcher --region "$$REGION" --format='value(status.url)'); \
	[ -n "$$URL" ] || { echo "[ERROR] deploy fetcher first"; exit 1; }; \
	SA_EMAIL="$(SCHED_SA)@$$PROJECT_ID.iam.gserviceaccount.com"; \
	if gcloud scheduler jobs describe "$(SCHED_JOB)" --location="$$REGION" >/dev/null 2>&1; then \
	  gcloud scheduler jobs update http "$(SCHED_JOB)" --location="$$REGION" --schedule="$(SCHED_CRON)" --uri="$$URL/run" --http-method=POST --oidc-service-account-email="$$SA_EMAIL" --oidc-token-audience="$$URL"; \
	else \
	  gcloud scheduler jobs create http "$(SCHED_JOB)" --location="$$REGION" --schedule="$(SCHED_CRON)" --uri="$$URL/run" --http-method=POST --oidc-service-account-email="$$SA_EMAIL" --oidc-token-audience="$$URL"; \
	fi; \
	echo "[OK] Scheduler: $(SCHED_JOB) (cron: $(SCHED_CRON)) -> $$URL/run"

.PHONY: scheduler_run_now
scheduler_run_now: check-env
	@gcloud scheduler jobs run "$(SCHED_JOB)" --location="$$REGION"

.PHONY: scheduler_info
scheduler_info: check-env
	@gcloud scheduler jobs describe "$(SCHED_JOB)" --location="$$REGION" --format=json

.PHONY: scheduler_down
scheduler_down: check-env
	- gcloud scheduler jobs delete "$(SCHED_JOB)" --location="$$REGION" -q
	@echo "[OK] Scheduler removed."

.PHONY: fetcher_private
fetcher_private: check-env
	@gcloud run services update-traffic weather-fetcher --region "$$REGION" --to-latest
	@gcloud run services update weather-fetcher --region "$$REGION" --no-allow-unauthenticated
	@echo "[OK] fetcher is now private."

.PHONY: run_once_auth
run_once_auth: check-env
	@URL=$$(gcloud run services describe weather-fetcher --region "$$REGION" --format='value(status.url)'); \
	[ -n "$$URL" ] || { echo "[ERROR] deploy fetcher first"; exit 1; }; \
	TOKEN=$$(gcloud auth print-identity-token); \
	curl -s -X POST "$$URL/run" -H "Authorization: Bearer $$TOKEN" | sed 's/.*/[OK] Ingestion triggered (auth)/'

# ===== Dashboard (Streamlit on Cloud Run) =====
.PHONY: build_dashboard
build_dashboard: check-env
	gcloud builds submit dashboard --tag gcr.io/$$PROJECT_ID/dashboard

.PHONY: deploy_dashboard
deploy_dashboard: check-env
	gcloud run deploy weather-dashboard \
	  --image gcr.io/$$PROJECT_ID/dashboard \
	  --region "$$REGION" \
	  --allow-unauthenticated

.PHONY: dashboard_url
dashboard_url: check-env
	@echo -n "weather-dashboard URL: "
	@gcloud run services describe weather-dashboard --region "$$REGION" --format='value(status.url)'

# ===== Dashboard local (Streamlit en local) =====

.PHONY: dash_venv
dash_venv:
	@python -m venv .venv
	@. .venv/Scripts/activate && pip install --upgrade pip
	@. .venv/Scripts/activate && pip install -r dashboard/requirements.txt db-dtypes
	@echo "import importlib, sys"            > .check_deps.py
	@echo "mods = ('google.cloud.bigquery','db_dtypes','pandas','pyarrow','streamlit')" >> .check_deps.py
	@echo "for m in mods:"                  >> .check_deps.py
	@echo "    try: importlib.import_module(m)" >> .check_deps.py
	@echo "    except Exception as e: print('[WARN]', m, 'import failed:', e, file=sys.stderr)" >> .check_deps.py
	@echo "print('[OK] deps installees')"   >> .check_deps.py
	@. .venv/Scripts/activate && python .check_deps.py
	@rm -f .check_deps.py

# Lance Streamlit en local (port 8501, plus robuste sous Windows)
.PHONY: dash_local
dash_local:
	@[ -n "$$PROJECT_ID" ] || { echo "[ERROR] PROJECT_ID manquant (charge .env avec 'make env-shell' ou exporte-le)"; exit 1; }
	@cd dashboard && GCP_PROJECT="$$PROJECT_ID" streamlit run app.py --server.port=8080 --server.address=localhost

# Ouvre le navigateur sur le bon port (essaie plusieurs méthodes selon l’OS/terminal)
.PHONY: dash_open
dash_open:
	@URL="http://localhost:8501"; \
	( command -v xdg-open >/dev/null 2>&1 && xdg-open "$$URL" ) || \
	( command -v open     >/dev/null 2>&1 && open "$$URL" )     || \
	powershell -NoProfile -Command "Start-Process '$$URL'" || true

# Variante Docker (mappe les identifiants ADC gcloud)
.PHONY: dash_local_docker
dash_local_docker:
	@[ -n "$$PROJECT_ID" ] || { echo "[ERROR] PROJECT_ID manquant"; exit 1; }
	docker build -t weather-dashboard:local ./dashboard
	docker run --rm -p 8501:8501 \
	  -e GCP_PROJECT="$$PROJECT_ID" \
	  -v "$${APPDATA}/gcloud":/root/.config/gcloud \
	  weather-dashboard:local


# ===== Teardown =====
.PHONY: stop_scheduler
stop_scheduler: check-env
	- gcloud scheduler jobs pause "$(SCHED_JOB)" --location "$$REGION" || true
	@echo "[OK] Scheduler paused."

.PHONY: step3_down
step3_down: check-env
	- gcloud scheduler jobs delete "$(SCHED_JOB)" --location="$$REGION" -q || true
	@echo "[OK] Scheduler job removed."

.PHONY: services_down
services_down: check-env
	- gcloud run services delete weather-fetcher --region "$$REGION" -q || true
	- gcloud run services delete weather-transformer --region "$$REGION" -q || true
	- gcloud run services delete weather-dashboard --region "$$REGION" -q || true
	@echo "[OK] Cloud Run services removed."

.PHONY: silver_down
silver_down: check-env
	- bq rm -f -t "$$PROJECT_ID:weather.observations" || true
	@echo "[OK] Silver table removed."

.PHONY: dataset_down
dataset_down: check-env
	- bq rm -f -d "$$PROJECT_ID:weather" || true
	@echo "[OK] Dataset 'weather' removed."

.PHONY: bronze_down
bronze_down: check-env
	- gsutil -m rm -r "gs://$$RAW_BUCKET" || true
	@echo "[OK] RAW bucket removed."

.PHONY: sa_down
sa_down: check-env
	- gcloud iam service-accounts delete "scheduler-caller@$$PROJECT_ID.iam.gserviceaccount.com" -q || true
	- gcloud iam service-accounts delete "pubsub-pusher@$$PROJECT_ID.iam.gserviceaccount.com" -q || true
	@echo "[OK] Service accounts removed."

.PHONY: gold_down
gold_down: check-env
	- bq rm -f -t "$$PROJECT_ID:weather.v_hourly_city" || true
	- bq rm -f -t "$$PROJECT_ID:weather.v_daily_city"  || true
	@echo "[OK] Gold views removed."

.PHONY: down_all
down_all: step3_down step2_down services_down gold_down silver_down dataset_down bronze_down sa_down
	@echo "[OK] Full teardown complete."

.PHONY: stop_all
stop_all: stop_scheduler
	@echo "[OK] Orchestration paused only."

.PHONY: postgres_stop
postgres_stop:
	- powershell -Command "Stop-Service postgresql* -ErrorAction SilentlyContinue" || true
	@echo "[OK] Local PostgreSQL stopped (if running)."

.PHONY: stop_everything
stop_everything: postgres_stop stop_all
	@echo "[OK] Everything stopped (cloud orchestration + local services)."