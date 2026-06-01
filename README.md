# Data Engineering & Analytics Portfolio

## Profile

Student at **42 Paris**, with a strong interest in:

- designing **data pipelines**
- **structuring and modeling** data
- **automating** workflows

---

## Key Skills

### Languages

- Python · SQL · R · Bash · C/C++

### Data Engineering & Orchestration

- Apache Airflow · Luigi · dbt · PySpark
- ETL / ELT · Ingestion · APIs
- Relational modeling · Medallion Architecture (Bronze / Silver / Gold)

### Databases & Storage

- PostgreSQL · BigQuery · DuckDB · SQLite · Supabase · Parquet

### Cloud & DevOps

- GCP (BigQuery, GCS, Cloud Run, Pub/Sub, Cloud Scheduler)
- Docker · Docker Compose · CI/CD

### Machine Learning & Computer Vision

- scikit-learn · TensorFlow · Keras · OpenCV
- Reinforcement Learning (Q-Learning, DQN) · Gymnasium

### Visualisation & BI

- Streamlit · Flask · Power BI · Shiny · Matplotlib · Seaborn

### Systems & Collaboration

- Linux · Git (GitHub, GitLab) · Bash automation

---

## Featured Projects

### Crypto Market Pulse - Real-Time Data Pipeline

<p align="center">
  <img src="crypto_market_pulse/assets/1.png" width="800"/><br/>
  <sub>Interactive dashboard</sub>
</p>

<br/>

<p align="center">
  <img src="crypto_market_pulse/assets/2.png" width="800"/><br/>
  <sub>Market sentiment tracking (Fear & Greed Index)</sub>
</p>

<br/>

<p align="center">
  <img src="crypto_market_pulse/assets/3.png" width="800"/><br/>
  <sub>Correlations and key indicators (RSI, volatility)</sub>
</p>

End-to-end pipeline to collect, transform and visualize **crypto data in near real-time**, exploring a key question: does market sentiment predict price movements?

- Automatic hourly collection of **BTC, ETH, BNB, SOL** prices (CoinGecko)
- Task orchestration with **Apache Airflow**
- Processing and computation of technical indicators (**RSI, volatility**) with **PySpark**
- **Bronze → Silver → Gold** layer modeling with **dbt**
- Storage in **PostgreSQL**, visualization with **Streamlit**
- Fully **Dockerized** environment

Folder: `crypto_market_pulse/`

---

### GCP Weather Pulse - Serverless Cloud Pipeline

<p align="center">
  <img src="gcp_weather_pulse/assets/tableau_de_bord1.png" width="800"/><br/>
  <sub>Weather dashboard</sub>
</p>

<br/>

<p align="center">
  <img src="gcp_weather_pulse/assets/tableau_de_bord2.png" width="800"/><br/>
  <sub>Weather trend analysis by city</sub>
</p>

Automated cloud pipeline to collect, transform and analyze **weather data**, fully hosted on Google Cloud with no infrastructure to manage.

- Automatic weather data collection via **Cloud Run**
- Execution scheduling with **Cloud Scheduler**
- Raw data storage in **GCS (Bronze)**
- Transformation and loading into **BigQuery (Silver)**
- Analytics-ready views (**Gold**)
- **Serverless**, automated and reproducible architecture

Folder: `gcp_weather_pulse/`

---

### Game Price Predictor - Machine Learning

<p align="center">
  <img src="price_sale_prediction/assets/UI.png" width="800"/><br/>
  <sub>Prediction interface</sub>
</p>

Machine Learning model to **predict the sale price of video games** based on their characteristics (platform, genre, release year, etc.).

- Data preparation and cleaning
- Modeling with **TensorFlow / Keras** (Deep Learning)
- Results: **R² = 0.90**, MAE = 4.70 €
- Performance evaluation (MAE, RMSE, R²)

Folder: `price_sale_prediction/`

---

### Product Sales Dashboard - Power BI

<p align="center">
  <img src="powerbi_product_dashboard/assets/dashboard_img.png" width="800"/><br/>
  <sub>Power BI dashboard</sub>
</p>

**Power BI** dashboard focused on commercial performance monitoring, designed as a realistic business case.

- Data modeling with a **star schema**
- Key indicators (**KPIs, ratios, margins**) calculated with **DAX**
- Trend analysis **week / month / quarter**
- Performance by salesperson, team and product category
- Design oriented towards **executive & decision-making reading**

Folder: `powerbi_product_dashboard/`

---

## Other Projects

### Anti-waste Shopify - Data Case Study

Technical case study completed in 2 hours for a **Data / Tech** position: turning operational data into concrete product display decisions on Shopify.

- Product data analysis (stock, expiry dates, sales)
- Calculation of an **anti-waste priority score** to rank products
- Generation of a **Shopify GraphQL** payload to reorder a collection
- Data storage with **Supabase** and analysis via **BigQuery**
- Mockup of an internal Ops / Marketing tool with KPIs and preview

Folder: `cas_pratique_willy_anti_gaspi/`

---

### Tennis Stats Tracker - Data Pipeline & Dashboard

<p align="center">
  <img src="tennis_stats_tracker/assets/photo1.png" width="800"/><br/>
  <sub>Player list</sub>
</p>

<br/>

<p align="center">
  <img src="tennis_stats_tracker/assets/photo2.png" width="800"/><br/>
  <sub>Full match table</sub>
</p>

<br/>

<p align="center">
  <img src="tennis_stats_tracker/assets/photo3.png" width="800"/><br/>
  <sub>Matches for the selected player</sub>
</p>

ETL pipeline and interactive application for analyzing **ATP tennis statistics**.

- Collection and cleaning of sports data (ATP)
- Relational modeling and **PostgreSQL** storage
- Analytical SQL queries
- Interactive dashboard with **Streamlit**
- **Dockerized** environment

Folder: `tennis_stats_tracker/`

---

### Rune OCR Analyzer - ML Image Analysis

<p align="center">
  <img src="rune_ocr_analyzer/assets/ui1.png" width="800"/><br/>
  <sub>Web interface</sub>
</p>

<br/>

<p align="center">
  <img src="rune_ocr_analyzer/assets/ui2.png" width="800"/><br/>
  <sub>Analysis results</sub>
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

Web application to **automatically analyze rune images** using OCR and business rules.

- Text recognition on images with **OCR**
- Automatic equivalence and score calculation
- Interactive web interface with **Flask**
- Logging and analysis history

Folder: `rune_ocr_analyzer/`

---

### Food Nutrition Pipeline - ETL & API

Automated data pipeline to extract and analyze **nutritional information** from food products.

- Data extraction via the **Open Food Facts** API
- ETL orchestration with **Luigi**
- XML data transformation and **Parquet + SQLite** storage
- Results exposed via a **Flask API**
- **Docker** deployment

Folder: `food_nutrition_pipeline/`

---

### NPS Prediction - Machine Learning & Text Mining

Customer feedback analysis to **predict the Net Promoter Score** and identify areas for improvement.

- Quantitative and textual customer data analysis
- **Text mining** and natural language processing
- Predictive modeling with **Random Forest**
- Interactive dashboard with **Shiny** (R)

Folder: `nps_prediction/`

---

### RL Agents - Reinforcement Learning

Multiple **reinforcement learning** agents applied to classic environments, up to a DQN agent playing Snake in real time.

- **Q-Learning** on CartPole, FrozenLake, MountainCar (Gymnasium)
- **DQN** agent with convolutional network (CNN) inspired by DeepMind Atari
- Real-time screen capture + **OCR** to read the score
- Training metrics tracking with **Pandas / Matplotlib**

Folder: `rl_agents/`

---

### Snake Agent RL - Training Data Analysis

<p align="center">
  <img src="snake_agent_rl/assets/demo_snake.gif" width="500"/><br/>
  <sub>Agent in action</sub>
</p>

<br/>

<p align="center">
  <img src="snake_agent_rl/assets/photo1.png" width="800"/><br/>
  <sub>Training metrics</sub>
</p>

<br/>

<p align="center">
  <img src="snake_agent_rl/assets/photo2.png" width="800"/><br/>
  <sub>Convergence curve</sub>
</p>

<br/>

<p align="center">
  <img src="snake_agent_rl/assets/photo3.png" width="800"/><br/>
  <sub>Exploration / exploitation analysis</sub>
</p>

Analysis of training data from a **Snake agent trained with reinforcement learning**.

- Custom environment based on **OpenAI Gym**
- Collection and analysis of **training metrics**
- Study of **convergence** and the exploration / exploitation trade-off
- Visualization and interpretation of agent performance

Folder: `snake_agent_rl/`

---

### Price Comparator - Multi-Source Aggregation

Tool to **compare product prices** by aggregating multiple heterogeneous data sources.

- Querying 3 distinct sources: **REST JSON API**, **XML**, **SerpAPI**
- Multi-format normalization (JSON, XML) into a unified DataFrame with **Pandas**
- Export results to **CSV** and **SQLite** database
- Price distribution visualization with **Matplotlib**

Folder: `comparateur_prix/`

---

### Mini Data Lake - Air Pollution

Demonstration of a **Data Lake** architecture to analyze air pollution data.

- CSV data cleaning and transformation
- Conversion to **optimized Parquet**
- Local and remote querying with **DuckDB**
- Visualization with **Matplotlib**

Folder: `mini_data_lake/`

---

## What I Put into Practice

- Designing **robust data pipelines**
- Database modeling and exploitation
- Workflow automation
- **Dockerized** environments
- Using **cloud** tools in real conditions

---

## Contact

- Email: **miguelfaucheux@hotmail.com**
- GitHub: https://github.com/Tee-Mig
- 42 Profile: https://cv.42.fr/fPu1xydA
