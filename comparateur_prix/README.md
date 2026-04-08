# Comparateur de Prix

Outil en ligne de commande pour comparer les prix d'un produit en interrogeant plusieurs sources hétérogènes (API JSON, XML, SerpAPI).  
Les résultats sont affichés, exportés (CSV + SQLite) et visualisés avec matplotlib.

---

## Fonctionnalités

- Interrogation de 3 sources de données distinctes :
  - **DummyJSON** — API REST JSON
  - **FakeStoreAPI** — données XML locales
  - **SerpAPI** — résultats de recherche web (clé API requise)
- Normalisation des données multi-format (JSON, XML) vers un DataFrame unifié
- Affichage tabulaire dans le terminal (via `tabulate`)
- Export des résultats en **CSV** et en base **SQLite**
- Génération d'une **visualisation matplotlib** de la distribution des prix

---

## Stack

- **Langage** : Python
- **Données** : pandas, XML (ElementTree), JSON
- **Stockage** : SQLite (via sqlite3 + SQLAlchemy), CSV
- **Visualisation** : matplotlib
- **APIs** : DummyJSON, FakeStoreAPI (XML local), SerpAPI
- **Utilitaires** : tabulate, python-dotenv, requests

---

## Structure du projet

```
comparateur_prix/
├── main.py                  # Point d'entrée — orchestration principale
├── db.py                    # Sauvegarde CSV et SQLite
├── visualisation.py         # Distribution des prix (matplotlib)
├── api_clients/
│   ├── supplier1.py         # Client DummyJSON (JSON)
│   ├── supplier2.py         # Client FakeStoreAPI (XML)
│   └── supplier3.py         # Client SerpAPI (JSON + clé API)
├── utils/
│   ├── api_utils.py         # Utilitaires HTTP
│   └── file_utils.py        # Chargement JSON/XML depuis fichier local
├── data/
│   ├── dummyjson.json        # Cache source 1
│   ├── fakestoreapi.xml      # Cache source 2
│   ├── serpapi.json          # Cache source 3
│   ├── result.csv            # Résultats exportés
│   └── products.db           # Base SQLite
└── requirements.txt
```

---

## Installation

```bash
git clone <repo>
cd comparateur_prix
pip install -r requirements.txt
```

### Configuration du `.env`

```bash
API_KEY_SERPAPI=ta_cle_serpapi
```

> Si les fichiers de cache (`data/*.json`, `data/*.xml`) sont présents, les APIs ne sont pas appelées.

---

## Utilisation

```bash
python main.py
```

L'outil demande le produit à rechercher (ex: `iPhone`, `laptop`).  
Taper `see` pour lister tous les produits disponibles dans les sources.

---

## Dépendances principales

- pandas
- matplotlib
- requests
- tabulate
- python-dotenv
- SQLAlchemy
- lxml