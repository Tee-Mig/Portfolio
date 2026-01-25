# Anti-gaspi Shopify – Case Study

Étude de cas visant à concevoir un outil permettant de réduire le gaspillage en e-commerce en priorisant automatiquement l’affichage des produits dans une collection Shopify à partir de données de stock, DDM et ventes.

## Contenu

### Partie 1 – Data & logique métier

- Analyse de données produit (stock, DDM, ventes)
- Calcul d’un **score de priorité anti-gaspi**
- Classement dynamique des produits
- Génération d’un payload Shopify GraphQL simulant le réordonnancement d’une collection

### Partie 2 – Conception produit

- Maquette d’un outil interne Ops / Marketing
- KPI clés, simulation, prévisualisation
- Publication contrôlée de l’ordre des produits sur Shopify

## Objectif

Transformer des données opérationnelles en décisions concrètes d’affichage produit, avec un contrôle humain avant publication.

## Technologies & sources

- Python
- Shopify (GraphQL – collections)
- Supabase (stock, DDM, prix)
- BigQuery (optionnel – ventes & analyses)

## Contexte

Projet réalisé dans le cadre d’une **étude de cas technique (2h)** pour un poste **Data / Tech**, avec une approche orientée **produit, data et opérationnelle**.
