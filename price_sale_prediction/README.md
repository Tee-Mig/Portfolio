# Game Price Predictor

Ce projet de Machine Learning utilise le Deep Learning (TensorFlow) pour **prédire le prix de vente de jeux vidéo** en fonction de caractéristiques comme la plateforme, le genre, l'année de sortie, etc.

## Installation

Installe les dépendances :

pip install -r requirements.txt

## 1. Préparation des données

À partir d'un fichier CSV brut dans data/raw/, exécute :

python scripts/prep_data.py \
 --input data/raw/games.csv \
 --output data/processed/processed_data.csv

## 2. Entraînement du modèle

python scripts/train_model.py \
 --data data/processed/processed_data.csv \
 --model_output models/model.keras

Sauvegarde automatiquement :

- le modèle TensorFlow model.keras
- le préprocesseur model.keras_preprocessor.pkl

## 3. Prédiction

python scripts/predict.py \
 --input data/processed/processed_data.csv \
 --model models/model.keras \
 --output outputs/predictions.csv
Le script ajoute une colonne predicted_price au CSV.

## 4. Évaluation (si la colonne target est présente)

python scripts/evaluate.py \
 --input outputs/predictions.csv
Affiche :

MAE (Mean Absolute Error)
RMSE (Root Mean Squared Error)
R² score (coefficient de détermination)

## Exemple de résultats

Évaluation du modèle :
MAE : 4.70 €
RMSE : 5.71 €
R² : 0.9034

## Technologies

- Python 3.10+
- TensorFlow / Keras
- Scikit-learn
- Pandas / NumPy
- Joblib
