# Price Comparator

A command-line tool to compare product prices by querying multiple heterogeneous sources (JSON API, XML, SerpAPI)
Results are displayed, exported (CSV + SQLite), and visualized with matplotlib

---

## Features

- Queries 3 distinct data sources:
  - **DummyJSON** — REST JSON API
  - **FakeStoreAPI** — local XML data
  - **SerpAPI** — web search results (API key required)
- Multi-format data normalization (JSON, XML) into a unified DataFrame
- Tabular display in the terminal (via `tabulate`)
- Export results to **CSV** and **SQLite** database
- Generation of a **matplotlib visualization** of the price distribution

---

## Stack

- **Language**: Python
- **Data**: pandas, XML (ElementTree), JSON
- **Storage**: SQLite (via sqlite3 + SQLAlchemy), CSV
- **Visualization**: matplotlib
- **APIs**: DummyJSON, FakeStoreAPI (local XML), SerpAPI
- **Utilities**: tabulate, python-dotenv, requests

---

## Project Structure

```
comparateur_prix/
├── main.py                  # Entry point — main orchestration
├── db.py                    # CSV and SQLite saving
├── visualisation.py         # Price distribution (matplotlib)
├── api_clients/
│   ├── supplier1.py         # DummyJSON client (JSON)
│   ├── supplier2.py         # FakeStoreAPI client (XML)
│   └── supplier3.py         # SerpAPI client (JSON + API key)
├── utils/
│   ├── api_utils.py         # HTTP utilities
│   └── file_utils.py        # Load JSON/XML from local file
├── data/
│   ├── dummyjson.json        # Source 1 cache
│   ├── fakestoreapi.xml      # Source 2 cache
│   ├── serpapi.json          # Source 3 cache
│   ├── result.csv            # Exported results
│   └── products.db           # SQLite database
└── requirements.txt
```

---

## Installation

```bash
git clone <repo>
cd comparateur_prix
pip install -r requirements.txt
```

### `.env` Configuration

```bash
API_KEY_SERPAPI=your_serpapi_key
```

> If cache files (`data/*.json`, `data/*.xml`) are present, the APIs are not called

---

## Usage

```bash
python main.py
```

The tool prompts for the product to search (e.g. `iPhone`, `laptop`)
Type `see` to list all available products across all sources

---

## Main Dependencies

- pandas
- matplotlib
- requests
- tabulate
- python-dotenv
- SQLAlchemy
- lxml
