# =======================================
#  Step 1: Ingestion -> GCS (Cloud Run)
#  Git Bash compatible (Windows)
# =======================================
SHELL := /usr/bin/bash
.ONESHELL:

# --- Default target list ---
.PHONY: help
help:
	@echo "Weather Pulse - Make targets"
	@echo ""
	@echo "[Env]"
	@echo "  make check-env              # verify required env vars (PROJECT_ID, REGION, RAW_BUCKET)"
	@echo "  make env-shell              # open an interactive shell with .env loaded"
	@echo "  make print-env              # print current env"
	@echo ""
	@echo "[Step 1 - Ingestion -> GCS]"
	@echo "  make init                   # set project + enable core APIs (Run/Build/Storage/Container Registry)"
	@echo "  make bucket                 # create RAW bucket if missing"
	@echo "  make build_fetcher          # build fetcher image via Cloud Build"
	@echo "  make deploy_fetcher         # deploy fetcher on Cloud Run (public)"
	@echo "  make fetcher_url            # print fetcher service URL"
	@echo "  make run_once               # trigger one ingestion (POST /run)"
	@echo "  make run_once_auth          # trigger /run with ID token (if fetcher is private)"
	@echo "  make logs_fetcher           # tail recent fetcher logs"
	@echo "  make check-payload          # list latest raw payload(s) in GCS"
	@echo "  make peek                   # pretty-print last payload.json"
	@echo "  make peek-cities            # print item count and city list from last payload"
	@echo "  make grant_gcs_role         # grant Storage Object Admin on bucket to fetcher service account"
	@echo "  make destroy                # delete fetcher service + RAW bucket (irreversible)"
	@echo ""
	@echo "[Step 2 - Transform -> BigQuery (Pub/Sub -> Cloud Run)]"
	@echo "  make enable_step2_apis      # enable BigQuery + Pub/Sub APIs"
	@echo "  make bq_dataset             # create BigQuery dataset 'weather' (EU)"
	@echo "  make bq_table               # create partitioned table weather.observations"
	@echo "  make build_transformer      # build transformer image"
	@echo "  make deploy_transformer     # deploy transformer on Cloud Run (private)"
	@echo "  make test_transformer       # call /process once with last GCS path (manual test)"
	@echo "  make pubsub_bind            # create topic/sub and bind push OIDC -> transformer (+ run.invoker)"
	@echo "  make grant_pubsub_publish   # allow fetcher to publish to Pub/Sub"
	@echo "  make redeploy_fetcher_pubsub# redeploy fetcher with PUBSUB_TOPIC env"
	@echo "  make logs_transformer       # tail recent transformer logs"
	@echo "  make demo_query             # count rows inserted over last 2 days"
	@echo "  make demo_query_save        # same as above but save JSON result to results/"
	@echo "  make demo_sample            # sample 10 latest rows from v_hourly_city"
	@echo "  make step2_down             # delete transformer + topic + subscription"
	@echo ""
	@echo "[Step 2.5 - Gold views]"
	@echo "  make gold_views             # create views: v_hourly_city, v_daily_city"
	@echo "  make demo_view_hourly       # sample latest rows from v_hourly_city"
	@echo "  make demo_view_daily        # sample latest rows from v_daily_city"
	@echo "  make gold_down              # drop gold views"
	@echo ""
	@echo "[Step 3 - Orchestration (Cloud Scheduler -> /run)]"
	@echo "  make enable_step3_apis      # enable Cloud Scheduler API"
	@echo "  make scheduler_sa_up        # create scheduler caller SA + grant run.invoker on fetcher"
	@echo "  make scheduler_up           # create/update cron job (OIDC -> /run)"
	@echo "  make scheduler_run_now      # run the job immediately (one-shot)"
	@echo "  make scheduler_info         # show job status/details"
	@echo "  make scheduler_down         # delete scheduler job"
	@echo "  make fetcher_private        # make fetcher private (no unauthenticated access)"
	@echo ""
	@echo "[Dashboard (Streamlit on Cloud Run) - optional]"
	@echo "  make build_dashboard        # build dashboard image"
	@echo "  make deploy_dashboard       # deploy dashboard (public)"
	@echo "  make dashboard_url          # print dashboard URL"
	@echo ""
	@echo "[Teardown / Cleanup]"
	@echo "  make stop_scheduler         # pause scheduler (safe stop)"
	@echo "  make services_down          # delete Cloud Run services (fetcher/transformer/dashboard)"
	@echo "  make silver_down            # drop silver table (weather.observations)"
	@echo "  make dataset_down           # drop dataset 'weather'"
	@echo "  make bronze_down            # delete RAW bucket"
	@echo "  make sa_down                # delete helper service accounts (scheduler-caller, pubsub-pusher)"
	@echo "  make step3_down             # delete scheduler job"
	@echo "  make down_all               # full teardown (Step 1/2/2.5/3 + SA + bucket)"
	@echo "  make stop_all               # pause orchestration only (no deletions)"


# ===== Step 1: Ingestion -> GCS (Cloud Run) =====

# --- Required env check ---
.PHONY: check-env
check-env:
	@if [ -z "$$PROJECT_ID" ] || [ -z "$$REGION" ] || [ -z "$$RAW_BUCKET" ]; then \
		echo "[ERROR] Missing variables. Load them via '.env' and 'make env-shell' (or export them)."; \
		echo "        Required: PROJECT_ID, REGION, RAW_BUCKET"; \
		exit 1; \
	else \
		echo "[OK] Variables found: PROJECT_ID=$$PROJECT_ID, REGION=$$REGION, RAW_BUCKET=$$RAW_BUCKET"; \
	fi

# --- Open an interactive shell with .env loaded (only for this subshell) ---
.PHONY: env-shell
env-shell:
	if [ ! -f .env ]; then
	  echo ".env not found. Create it first." >&2
	  exit 1
	fi
	echo "Opening an interactive shell with .env loaded (type 'exit' to quit)..."
	set -a            # allexport
	. ./.env          # POSIX: equivalent to 'source .env'
	set +a
	exec bash -i

# --- Print current env ---
.PHONY: print-env
print-env: check-env
	@echo "PROJECT_ID=$$PROJECT_ID"
	@echo "REGION=$$REGION"
	@echo "RAW_BUCKET=gs://$$RAW_BUCKET"

# --- Project init + APIs ---
.PHONY: init
init: check-env
	gcloud config set project "$$PROJECT_ID"
	gcloud services enable run.googleapis.com cloudbuild.googleapis.com storage.googleapis.com containerregistry.googleapis.com

# --- Create GCS bucket if missing ---
.PHONY: bucket
bucket: check-env
	@echo "Creating bucket if needed: gs://$$RAW_BUCKET"
	@gsutil ls -b "gs://$$RAW_BUCKET" >/dev/null 2>&1 || gsutil mb -p "$$PROJECT_ID" -l "$$REGION" "gs://$$RAW_BUCKET"
	@gsutil ls -b "gs://$$RAW_BUCKET"

# --- Build fetcher image (Cloud Build) ---
.PHONY: build_fetcher
build_fetcher: check-env
	gcloud builds submit fetcher --tag gcr.io/$$PROJECT_ID/fetcher

# --- Deploy fetcher on Cloud Run (no Pub/Sub) ---
.PHONY: deploy_fetcher
deploy_fetcher: check-env
	gcloud run deploy weather-fetcher \
	  --image gcr.io/$$PROJECT_ID/fetcher \
	  --region "$$REGION" \
	  --allow-unauthenticated \
	  --set-env-vars RAW_BUCKET=$$RAW_BUCKET

# --- Get service URL ---
.PHONY: fetcher_url
fetcher_url: check-env
	@echo -n "weather-fetcher URL: "
	@gcloud run services describe weather-fetcher --region "$$REGION" --format='value(status.url)'

# --- Trigger one ingestion (POST /run) ---
.PHONY: run_once
run_once: check-env
	@URL=$$(gcloud run services describe weather-fetcher --region "$$REGION" --format='value(status.url)'); \
	if [ -z "$$URL" ]; then echo "[ERROR] Service not found. Deploy first: make deploy_fetcher"; exit 1; fi; \
	powershell -NoProfile -Command "Invoke-WebRequest -UseBasicParsing -Method POST -Uri '$$URL/run' | Out-Null; Write-Output '[OK] Ingestion triggered'"

# --- Fetcher logs ---
.PHONY: logs_fetcher
logs_fetcher: check-env
	gcloud run services logs read weather-fetcher --region "$$REGION" --limit 100

.PHONY: check_payload
check-payload: check-env
	gsutil ls -r "gs://$$RAW_BUCKET/raw/**/payload.json"

.PHONY: peek
peek: check-env
	@LAST=$$(gsutil ls -r "gs://$$RAW_BUCKET/raw/**/payload.json" | tail -n 1)
	@echo "[peek] $$LAST"
	@gsutil cat "$$LAST" | python -m json.tool | less

# save json file as .peek.json
.PHONY: peek-cities
peek-cities: check-env
	@echo "[env] RAW_BUCKET=$$RAW_BUCKET"
	@LAST=$$(gsutil ls -r "gs://$$RAW_BUCKET/raw/**/payload.json" | tail -n 1); \
	if [ -z "$$LAST" ]; then echo "[peek-cities] no payload found under gs://$$RAW_BUCKET/raw/"; exit 1; fi; \
	echo "[peek-cities] $$LAST"; \
	if ! gsutil cat "$$LAST" > .peek.json 2>/dev/null; then \
	  echo "[peek-cities] gsutil cat failed (permissions or missing object)"; exit 1; \
	fi; \
		python - <<'PY' || { echo "[peek-cities] JSON parse failed (printing first 200 chars)"; head -c 200 .peek.json; echo; exit 1; }
	import json, sys
	with open(".peek.json","rb") as f:
		data = json.load(f)
	print("items:", len(data))
	print("cities:", [d.get("city") for d in data][:10])
	PY
		@rm -f .peek.json

# --- Grant GCS role to service account if 403 on upload ---
.PHONY: grant_gcs_role
grant_gcs_role: check-env
	@SA=$$(gcloud run services describe weather-fetcher --region "$$REGION" --format='value(spec.template.spec.serviceAccountName)'); \
	if [ -z "$$SA" ]; then echo "[ERROR] Service not deployed."; exit 1; fi; \
	echo "Granting roles/storage.objectAdmin to $$SA on gs://$$RAW_BUCKET"; \
	gsutil iam ch serviceAccount:$$SA:roles/storage.objectAdmin "gs://$$RAW_BUCKET"; \
	echo "[OK] Role granted."

# --- Cleanup (Step 1 only) ---
.PHONY: destroy
destroy: check-env
	- gcloud run services delete weather-fetcher --region "$$REGION" -q
	- gsutil -m rm -r "gs://$$RAW_BUCKET" || true
	@echo "[OK] Step 1 cleaned up."


# ===== Step 2: Transform -> BigQuery (Pub/Sub -> Cloud Run) =====

# Required services: BigQuery + Pub/Sub
.PHONY: enable_step2_apis
enable_step2_apis: check-env
	gcloud services enable bigquery.googleapis.com pubsub.googleapis.com

# Create BigQuery dataset
.PHONY: bq_dataset
bq_dataset: check-env
	@TOKEN=$$(gcloud auth print-access-token); \
	OUT=.bq_create_dataset.json; \
	CODE=$$(curl -s -o $$OUT -w '%{http_code}' -X POST \
	  -H "Authorization: Bearer $$TOKEN" \
	  -H "Content-Type: application/json" \
	  -d '{ \
	        "datasetReference": {"datasetId":"weather","projectId":"'"$$PROJECT_ID"'"}, \
	        "location":"EU", \
	        "friendlyName":"Weather curated dataset" \
	      }' \
	  "https://bigquery.googleapis.com/bigquery/v2/projects/$$PROJECT_ID/datasets"); \
	if [ "$$CODE" = "200" ] || [ "$$CODE" = "409" ]; then \
	  echo "[OK] Dataset 'weather' created (or already exists) (HTTP $$CODE)"; \
	else \
	  echo "[ERROR] Dataset creation failed (HTTP $$CODE)"; \
	  cat $$OUT; echo; \
	  rm -f $$OUT; exit 1; \
	fi; \
	rm -f $$OUT

# Create BigQuery table (partitioned by DATE(ts))
.PHONY: bq_table
bq_table: check-env
	@TOKEN=$$(gcloud auth print-access-token); \
	OUT=.bq_create_table.json; \
	CODE=$$(curl -s -o $$OUT -w '%{http_code}' -X POST \
	  -H "Authorization: Bearer $$TOKEN" \
	  -H "Content-Type: application/json" \
	  -d '{ \
	        "tableReference": {"projectId":"'"$$PROJECT_ID"'","datasetId":"weather","tableId":"observations"}, \
	        "timePartitioning": {"type":"DAY","field":"ts"}, \
	        "schema": {"fields":[ \
	          {"name":"city","type":"STRING","mode":"REQUIRED"}, \
	          {"name":"ts","type":"TIMESTAMP","mode":"REQUIRED"}, \
	          {"name":"temperature_2m","type":"FLOAT","mode":"NULLABLE"}, \
	          {"name":"relative_humidity_2m","type":"FLOAT","mode":"NULLABLE"}, \
	          {"name":"precipitation","type":"FLOAT","mode":"NULLABLE"}, \
	          {"name":"wind_speed_10m","type":"FLOAT","mode":"NULLABLE"} \
	        ]} \
	      }' \
	  "https://bigquery.googleapis.com/bigquery/v2/projects/$$PROJECT_ID/datasets/weather/tables"); \
	if [ "$$CODE" = "200" ] || [ "$$CODE" = "409" ]; then \
	  echo "[OK] Table 'weather.observations' ready (HTTP $$CODE)"; \
	else \
	  echo "[ERROR] Table creation failed (HTTP $$CODE)"; \
	  cat $$OUT; echo; \
	  rm -f $$OUT; exit 1; \
	fi; \
	rm -f $$OUT


# Build transformer image
.PHONY: build_transformer
build_transformer: check-env
	gcloud builds submit transformer --tag gcr.io/$$PROJECT_ID/transformer

.PHONY: test_transformer
test_transformer: check-env
	@URL=$$(gcloud run services describe weather-transformer --region "$$REGION" --format='value(status.url)'); \
	if [ -z "$$URL" ]; then echo "[ERROR] transformer not deployed"; exit 1; fi; \
	LAST=$$(gsutil ls -r "gs://$$RAW_BUCKET/raw/**/payload.json" | tail -n 1); \
	if [ -z "$$LAST" ]; then echo "[ERROR] no payload found in gs://$$RAW_BUCKET/raw/"; exit 1; fi; \
	PATH_IN_BUCKET=$${LAST#gs://$$RAW_BUCKET/}; \
	echo "[test_transformer] POST $$URL/process with path=$$PATH_IN_BUCKET"; \
	curl -s -X POST "$$URL/process" \
	  -H "Content-Type: application/json" \
	  -d '{"message":{"attributes":{"path":"'"'"'$$PATH_IN_BUCKET'"'"'}}}' \
	  | sed 's/^/[resp] /'

.PHONY: deploy_transformer
deploy_transformer: check-env
	gcloud run deploy weather-transformer \
	  --image gcr.io/$$PROJECT_ID/transformer \
	  --region "$$REGION" \
	  --no-allow-unauthenticated \
	  --set-env-vars PROJECT_ID=$$PROJECT_ID,BQ_DATASET=weather,BQ_TABLE=observations,RAW_BUCKET=$$RAW_BUCKET


# Create Pub/Sub topic and push subscription to transformer
.PHONY: pubsub_bind
pubsub_bind: check-env
	@URL=$$(gcloud run services describe weather-transformer --region "$$REGION" --format='value(status.url)'); \
	if [ -z "$$URL" ]; then echo "[ERROR] transformer not deployed"; exit 1; fi; \
	SA_EMAIL="pubsub-pusher@$$PROJECT_ID.iam.gserviceaccount.com"; \
	# 0) Topic (ignore if exists)
	gcloud pubsub topics create weather-transform >/dev/null 2>&1 || true; \
	# 1) Ensure a service account for OIDC
	gcloud iam service-accounts describe $$SA_EMAIL >/dev/null 2>&1 || \
	  gcloud iam service-accounts create pubsub-pusher --display-name="Pub/Sub push SA"; \
	# 2) Allow this SA to invoke the Cloud Run service
	gcloud run services add-iam-policy-binding weather-transformer \
	  --region "$$REGION" \
	  --member="serviceAccount:$$SA_EMAIL" \
	  --role="roles/run.invoker" >/dev/null; \
	# 3) Recreate subscription to refresh auth mode/endpoints
	gcloud pubsub subscriptions delete weather-transform-sub -q >/dev/null 2>&1 || true; \
	gcloud pubsub subscriptions create weather-transform-sub \
	  --topic=weather-transform \
	  --push-endpoint="$$URL/process" \
	  --push-auth-service-account="$$SA_EMAIL"; \
	echo "[OK] Pub/Sub wired with OIDC: weather-transform-sub -> $$URL/process (as $$SA_EMAIL)"

# Allow fetcher to publish to Pub/Sub
.PHONY: grant_pubsub_publish
grant_pubsub_publish: check-env
	SA=$$(gcloud run services describe weather-fetcher --region "$$REGION" --format='value(spec.template.spec.serviceAccountName)'); \
	if [ -z "$$SA" ]; then echo "[ERROR] weather-fetcher not deployed"; exit 1; fi; \
	gcloud projects add-iam-policy-binding "$$PROJECT_ID" \
	  --member="serviceAccount:$$SA" \
	  --role="roles/pubsub.publisher"

# (Re)deploy fetcher with PUBSUB_TOPIC so it publishes the path for step 2
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

# --- Count rows over last 2 days (Windows/Git Bash safe; avoids backtick expansion)
.PHONY: demo_query
demo_query: check-env
	@TOKEN=$$(gcloud auth print-access-token); \
	printf 'SELECT COUNT(*) AS n FROM `%s.weather.observations` WHERE DATE(ts) >= DATE_SUB(CURRENT_DATE(), INTERVAL 2 DAY)\n' "$$PROJECT_ID" > .query.sql; \
	python -c "import json,io; q=io.open('.query.sql','r',encoding='utf-8').read(); io.open('.body.json','w',encoding='utf-8').write(json.dumps({'query': q, 'useLegacySql': False}))"; \
	curl -s -X POST \
	  -H "Authorization: Bearer $$TOKEN" -H "Content-Type: application/json" \
	  -d @.body.json \
	  "https://bigquery.googleapis.com/bigquery/v2/projects/$$PROJECT_ID/queries" > .resp.json; \
	python -c "import json,io,sys; r=json.load(io.open('.resp.json','rb')); print('rows:', r.get('rows',[{'f':[{'v':0}]}])[0]['f'][0]['v']) if 'rows' in r else (print(r),sys.exit(1))"; \
	rm -f .query.sql .body.json .resp.json

# Save the JSON response to results/observations_count.json
.PHONY: demo_query_save
demo_query_save: check-env
	@mkdir -p results
	@TOKEN=$$(gcloud auth print-access-token); \
	printf 'SELECT COUNT(*) AS n FROM `%s.weather.observations` WHERE DATE(ts) >= DATE_SUB(CURRENT_DATE(), INTERVAL 2 DAY)\n' "$$PROJECT_ID" > results.query.sql; \
	python -c "import json,io; q=io.open('results.query.sql','r',encoding='utf-8').read(); io.open('results.body.json','w',encoding='utf-8').write(json.dumps({'query': q, 'useLegacySql': False}))"; \
	curl -s -X POST \
	  -H "Authorization: Bearer $$TOKEN" -H "Content-Type: application/json" \
	  -d @results.body.json \
	  "https://bigquery.googleapis.com/bigquery/v2/projects/$$PROJECT_ID/queries" \
	  > results/observations_count.json; \
	python -c "import json; r=json.load(open('results/observations_count.json','rb')); print('rows:', r['rows'][0]['f'][0]['v']) if 'rows' in r else print(r)"
	@echo "Saved: results/observations_count.json"

# --- Sample 10 latest rows (Windows/Git Bash safe; no jq, no heredoc)
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
	curl -s -X POST \
	  -H "Authorization: Bearer $$TOKEN" -H "Content-Type: application/json" \
	  -d @.body.json \
	  "https://bigquery.googleapis.com/bigquery/v2/projects/$$PROJECT_ID/queries" > .resp.json; \
	python -c "import json,io,sys; r=json.load(io.open('.resp.json','rb')); print('\n'.join([f\"{row['f'][0]['v']}\t{row['f'][1]['v']}\t{row['f'][2]['v']}\" for row in r.get('rows',[])])) if 'rows' in r else (print(r),sys.exit(1))"; \
	rm -f .query.sql .body.json .resp.json


.PHONY: step2_down
step2_down: check-env
	- gcloud pubsub subscriptions delete weather-transform-sub -q || true
	- gcloud pubsub topics delete weather-transform -q || true
	- gcloud run services delete weather-transformer --region "$$REGION" -q || true
	@echo "[OK] Step 2 removed."

# ===== Gold Views (via REST API: jobs.query) =====
# Crée des vues BigQuery avec CREATE OR REPLACE VIEW, sans bq, compatible Git Bash/Windows
# Prérequis: dataset 'weather' et table 'observations' existent (bq_dataset / bq_table)

.PHONY: gold_hourly_view
gold_hourly_view: check-env
	@TOKEN=$$(gcloud auth print-access-token); \
	# SQL: v_hourly_city (sélection propre des colonnes utiles)
	printf 'CREATE OR REPLACE VIEW `'$${PROJECT_ID}'.weather.v_hourly_city` AS\n' > .view_hourly.sql; \
	printf 'SELECT city, ts, temperature_2m, relative_humidity_2m, precipitation, wind_speed_10m\n' >> .view_hourly.sql; \
	printf 'FROM `'$${PROJECT_ID}'.weather.observations`;\n' >> .view_hourly.sql; \
	# Construire le body JSON
	python -c "import json,io; q=io.open('.view_hourly.sql','r',encoding='utf-8').read(); io.open('.view_hourly.body.json','w',encoding='utf-8').write(json.dumps({'query': q, 'useLegacySql': False}))"; \
	# Appel API
	curl -s -X POST \
	  -H "Authorization: Bearer $$TOKEN" -H "Content-Type: application/json" \
	  -d @.view_hourly.body.json \
	  "https://bigquery.googleapis.com/bigquery/v2/projects/$$PROJECT_ID/queries" \
	  > .view_hourly.resp.json; \
	# Feedback minimal
	python -c "import json; r=json.load(open('.view_hourly.resp.json','rb')); print('[OK] v_hourly_city created') if 'jobComplete' in r or 'rows' in r else print(r)"; \
	rm -f .view_hourly.sql .view_hourly.body.json .view_hourly.resp.json

.PHONY: gold_daily_view
gold_daily_view: check-env gold_hourly_view
	@TOKEN=$$(gcloud auth print-access-token); \
	# SQL: v_daily_city (agrégations par jour)
	printf 'CREATE OR REPLACE VIEW `'$${PROJECT_ID}'.weather.v_daily_city` AS\n' > .view_daily.sql; \
	printf 'SELECT city,\n' >> .view_daily.sql; \
	printf '       DATE(ts) AS day,\n' >> .view_daily.sql; \
	printf '       AVG(temperature_2m)       AS avg_temp,\n' >> .view_daily.sql; \
	printf '       AVG(relative_humidity_2m) AS avg_humidity,\n' >> .view_daily.sql; \
	printf '       SUM(precipitation)        AS total_precip,\n' >> .view_daily.sql; \
	printf '       AVG(wind_speed_10m)       AS avg_wind\n' >> .view_daily.sql; \
	printf 'FROM `'$${PROJECT_ID}'.weather.v_hourly_city`\n' >> .view_daily.sql; \
	printf 'GROUP BY city, day;\n' >> .view_daily.sql; \
	# Construire le body JSON
	python -c "import json,io; q=io.open('.view_daily.sql','r',encoding='utf-8').read(); io.open('.view_daily.body.json','w',encoding='utf-8').write(json.dumps({'query': q, 'useLegacySql': False}))"; \
	# Appel API
	curl -s -X POST \
	  -H "Authorization: Bearer $$TOKEN" -H "Content-Type: application/json" \
	  -d @.view_daily.body.json \
	  "https://bigquery.googleapis.com/bigquery/v2/projects/$$PROJECT_ID/queries" \
	  > .view_daily.resp.json; \
	# Feedback minimal
	python -c "import json; r=json.load(open('.view_daily.resp.json','rb')); print('[OK] v_daily_city created') if 'jobComplete' in r or 'rows' in r else print(r)"; \
	rm -f .view_daily.sql .view_daily.body.json .view_daily.resp.json

.PHONY: gold_views
gold_views: check-env gold_hourly_view gold_daily_view
	@echo "[OK] Gold views ready: weather.v_hourly_city, weather.v_daily_city"

.PHONY: demo_view_hourly
demo_view_hourly: check-env
	@TOKEN=$$(gcloud auth print-access-token); \
	printf 'SELECT city, ts, temperature_2m FROM `%s.weather.v_hourly_city` ORDER BY ts DESC LIMIT 10\n' "$$PROJECT_ID" > .q.sql; \
	python -c "import json,io; q=io.open('.q.sql','r',encoding='utf-8').read(); io.open('.b.json','w',encoding='utf-8').write(json.dumps({'query': q, 'useLegacySql': False}))"; \
	curl -s -X POST -H "Authorization: Bearer $$TOKEN" -H "Content-Type: application/json" \
	  -d @.b.json "https://bigquery.googleapis.com/bigquery/v2/projects/$$PROJECT_ID/queries" > .r.json; \
	python -c "import json,io; r=json.load(io.open('.r.json','rb')); \
print('\n'.join([f\"{row['f'][0]['v']}\t{row['f'][1]['v']}\t{row['f'][2]['v']}\" for row in r.get('rows',[])])) if 'rows' in r else print(r)"; \
	rm -f .q.sql .b.json .r.json

.PHONY: demo_view_daily
demo_view_daily: check-env
	@TOKEN=$$(gcloud auth print-access-token); \
	printf 'SELECT city, day, avg_temp, total_precip, avg_wind FROM `%s.weather.v_daily_city` ORDER BY day DESC, city LIMIT 10\n' "$$PROJECT_ID" > .q.sql; \
	python -c "import json,io; q=io.open('.q.sql','r',encoding='utf-8').read(); io.open('.b.json','w',encoding='utf-8').write(json.dumps({'query': q, 'useLegacySql': False}))"; \
	curl -s -X POST -H "Authorization: Bearer $$TOKEN" -H "Content-Type: application/json" \
	  -d @.b.json "https://bigquery.googleapis.com/bigquery/v2/projects/$$PROJECT_ID/queries" > .r.json; \
	python -c "import json,io; r=json.load(io.open('.r.json','rb')); \
print('\n'.join([f\"{row['f'][0]['v']}\t{row['f'][1]['v']}\tT:{row['f'][2]['v']}\tP:{row['f'][3]['v']}\tW:{row['f'][4]['v']}\" for row in r.get('rows',[])])) if 'rows' in r else print(r)"; \
	rm -f .q.sql .b.json .r.json

# ===== Step 3: Orchestration (Cloud Scheduler -> Cloud Run /run) =====
# Variables (tu peux changer la fréquence CRON ici)
SCHED_CRON ?= 0 * * * *     # toutes les heures
SCHED_JOB  ?= fetch-hourly-weather
SCHED_SA   ?= scheduler-caller

# 0) Activer l’API Scheduler (une fois)
.PHONY: enable_step3_apis
enable_step3_apis: check-env
	@gcloud services enable cloudscheduler.googleapis.com

# 1) Créer/assurer le service account qui signera l’OIDC + lui donner run.invoker sur le fetcher
.PHONY: scheduler_sa_up
scheduler_sa_up: check-env
	@SA_EMAIL="$(SCHED_SA)@$$PROJECT_ID.iam.gserviceaccount.com"; \
	gcloud iam service-accounts describe $$SA_EMAIL >/dev/null 2>&1 || \
	  gcloud iam service-accounts create "$(SCHED_SA)" --display-name="Cloud Scheduler caller"; \
	gcloud run services add-iam-policy-binding weather-fetcher \
	  --region "$$REGION" \
	  --member="serviceAccount:$$SA_EMAIL" \
	  --role="roles/run.invoker" >/dev/null; \
	echo "[OK] Scheduler SA ready: $$SA_EMAIL (has roles/run.invoker on weather-fetcher)"

# 2) Créer/mettre à jour le job Scheduler (OIDC -> POST /run)
.PHONY: scheduler_up
scheduler_up: check-env scheduler_sa_up
	@URL=$$(gcloud run services describe weather-fetcher --region "$$REGION" --format='value(status.url)'); \
	if [ -z "$$URL" ]; then echo "[ERROR] weather-fetcher not deployed"; exit 1; fi; \
	SA_EMAIL="$(SCHED_SA)@$$PROJECT_ID.iam.gserviceaccount.com"; \
	if gcloud scheduler jobs describe "$(SCHED_JOB)" --location="$$REGION" >/dev/null 2>&1; then \
	  gcloud scheduler jobs update http "$(SCHED_JOB)" \
	    --location="$$REGION" \
	    --schedule="$(SCHED_CRON)" \
	    --uri="$$URL/run" \
	    --http-method=POST \
	    --oidc-service-account-email="$$SA_EMAIL" \
	    --oidc-token-audience="$$URL"; \
	else \
	  gcloud scheduler jobs create http "$(SCHED_JOB)" \
	    --location="$$REGION" \
	    --schedule="$(SCHED_CRON)" \
	    --uri="$$URL/run" \
	    --http-method=POST \
	    --oidc-service-account-email="$$SA_EMAIL" \
	    --oidc-token-audience="$$URL"; \
	fi; \
	echo "[OK] Cloud Scheduler job ready: $(SCHED_JOB) (cron: $(SCHED_CRON)) -> $$URL/run"

# 3) Lancer le job à la demande (utile pour test immédiat)
.PHONY: scheduler_run_now
scheduler_run_now: check-env
	@gcloud scheduler jobs run "$(SCHED_JOB)" --location="$$REGION"

# 4) Voir l’état du job (dernier run, prochaine exécution, etc.)
.PHONY: scheduler_info
scheduler_info: check-env
	@gcloud scheduler jobs describe "$(SCHED_JOB)" --location="$$REGION" --format=json

# 5) Supprimer le job Scheduler (cleanup)
.PHONY: scheduler_down
scheduler_down: check-env
	- gcloud scheduler jobs delete "$(SCHED_JOB)" --location="$$REGION" -q
	@echo "[OK] Scheduler job removed."

# (Optionnel) 6) Rendre le fetcher privé et fournir un run_once authentifié
.PHONY: fetcher_private
fetcher_private: check-env
	@gcloud run services update-traffic weather-fetcher --region "$$REGION" --to-latest
	@gcloud run services update weather-fetcher --region "$$REGION" --no-allow-unauthenticated
	@echo "[OK] weather-fetcher is now private (requires roles/run.invoker via OIDC)."

# (Optionnel) 7) Déclencher /run avec ID token (utile si fetcher privé)
.PHONY: run_once_auth
run_once_auth: check-env
	@URL=$$(gcloud run services describe weather-fetcher --region "$$REGION" --format='value(status.url)'); \
	if [ -z "$$URL" ]; then echo "[ERROR] weather-fetcher not deployed"; exit 1; fi; \
	TOKEN=$$(gcloud auth print-identity-token); \
	curl -s -X POST "$$URL/run" -H "Authorization: Bearer $$TOKEN" | sed 's/.*/[OK] Ingestion triggered (auth)/'

# ===== Dashboard (Streamlit -> Cloud Run) =====

.PHONY: build_dashboard
build_dashboard: check-env
	gcloud builds submit dashboard --tag gcr.io/$$PROJECT_ID/dashboard

.PHONY: deploy_dashboard
deploy_dashboard: check-env
	# Récupère le service account courant du fetcher pour réutiliser les mêmes droits BQ si tu veux
	# (optionnel, sinon Cloud Run utilisera le compte par défaut du projet)
	gcloud run deploy weather-dashboard \
	  --image gcr.io/$$PROJECT_ID/dashboard \
	  --region "$$REGION" \
	  --allow-unauthenticated

.PHONY: dashboard_url
dashboard_url: check-env
	@echo -n "weather-dashboard URL: "
	@gcloud run services describe weather-dashboard --region "$$REGION" --format='value(status.url)'

# ===== Teardown (stop / delete all) =====

.PHONY: stop_scheduler
stop_scheduler: check-env
	- gcloud scheduler jobs pause fetch-hourly-weather --location "$$REGION" || true
	@echo "[OK] Scheduler paused (safe stop)."

.PHONY: step3_down
step3_down: check-env
	- gcloud scheduler jobs delete fetch-hourly-weather --location "$$REGION" -q || true
	@echo "[OK] Scheduler job removed."

.PHONY: services_down
services_down: check-env
	- gcloud run services delete weather-fetcher --region "$$REGION" -q || true
	- gcloud run services delete weather-transformer --region "$$REGION" -q || true
	- gcloud run services delete weather-dashboard --region "$$REGION" -q || true
	@echo "[OK] Cloud Run services removed."

.PHONY: gold_down
gold_down: check-env
	- bq rm -f -t "$$PROJECT_ID:weather.v_hourly_city" || true
	- bq rm -f -t "$$PROJECT_ID:weather.v_daily_city"  || true
	@echo "[OK] Gold views removed."

.PHONY: silver_down
silver_down: check-env
	- bq rm -f -t "$$PROJECT_ID:weather.observations" || true
	@echo "[OK] Silver table removed."

.PHONY: dataset_down
dataset_down: check-env
	- bq rm -f -d "$$PROJECT_ID:weather" || true
	@echo "[OK] BigQuery dataset 'weather' removed."

.PHONY: bronze_down
bronze_down: check-env
	- gsutil -m rm -r "gs://$$RAW_BUCKET" || true
	@echo "[OK] GCS RAW bucket removed (bronze)."

.PHONY: sa_down
sa_down: check-env
	- gcloud iam service-accounts delete "scheduler-caller@$$PROJECT_ID.iam.gserviceaccount.com" -q || true
	- gcloud iam service-accounts delete "pubsub-pusher@$$PROJECT_ID.iam.gserviceaccount.com" -q || true
	@echo "[OK] Service accounts removed."

.PHONY: down_all
down_all: step3_down step2_down services_down gold_down silver_down dataset_down bronze_down sa_down
	@echo "[OK] Full teardown complete."

# One-shots
.PHONY: stop_all
stop_all: stop_scheduler
	@echo "[OK] Orchestration paused only (no deletions)."
