import os
import logging
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
logging.getLogger('tensorflow').setLevel(logging.ERROR)

import argparse
import pandas as pd
import tensorflow as tf
import joblib

def main(args):
    print("Chargement des nouvelles données")
    df = pd.read_csv(args.input)

    X = df.drop(columns=["title"], errors='ignore')

    print("Chargement du préprocesseur")
    preprocessor_path = args.model + "_preprocessor.pkl"
    if not os.path.exists(preprocessor_path):
        raise FileNotFoundError(f"Préprocesseur non trouvé : {preprocessor_path}")
    preprocessor = joblib.load(preprocessor_path)

    print("Transformation des données")
    X_processed = preprocessor.transform(X)

    print("Chargement du modèle")
    model = tf.keras.models.load_model(args.model)

    print("Prédiction")
    predictions = model.predict(X_processed).flatten()

    df["predicted_price"] = predictions

    print(f"Sauvegarde des prédictions dans {args.output} ")
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    df.to_csv(args.output, index=False)
    print("Prédictions terminées.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prédictions avec modèle TensorFlow")
    parser.add_argument('--input', type=str, required=True, help="CSV avec les données à prédire")
    parser.add_argument('--model', type=str, required=True, help="Fichier du modèle (.keras ou .h5)")
    parser.add_argument('--output', type=str, required=True, help="Fichier de sortie avec les prédictions")
    args = parser.parse_args()
    main(args)