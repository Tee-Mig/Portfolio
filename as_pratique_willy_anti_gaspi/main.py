import json
import math
from datetime import date
import pandas as pd

CSV_PATH = "./Jeu_de_donnees.csv"

# --- Shopify (simulation) ---
COLLECTION_GID = "gid://shopify/Collection/1234567890"
TOP_N = 50  # nombre de produits à repositionner parmis ceux avec le meilleur score
PREVIEW_NUMBER = 20

def compute_score(row, today: date) -> float:
    """
    Score merchandising:
    - DDM proche => plus haut
    - Stock élevé => plus haut
    - Faible quantité vendue => plus haut (lent à partir)
    - Rupture stock => tout en bas
    """
    stock = int(row["produit_en_ligne_stock_actuel"])
    sold = int(row["quantite_vendue"])

    if stock <= 0:
        return -2147483648 # tout en bas car pas de stock

    ddm = row["produit_en_ligne_ddm"]
    if pd.isna(ddm):
        days_to_ddm = 10_000  # pas urgent si pas de DDM
    else:
        days_to_ddm = (ddm - today).days

    # si DDM déjà dépassée -> très urgent
    ddm_days = max(days_to_ddm, 0)
    ddm_score = 1.0 / (1.0 + ddm_days)

    stock_score = math.log1p(stock)
    slow_score = 1.0 / (1.0 + sold)

    score = 0.45 * ddm_score + 0.30 * stock_score + 0.25 * slow_score
    return score

def make_shopify_payload(collection_gid: str, moves: list[dict]) -> dict:
    """
    Payload GraphQL pour mutation collectionReorderProducts.
    """
    query = """
    mutation Reorder($id: ID!, $moves: [MoveInput!]!) {
      collectionReorderProducts(id: $id, moves: $moves) {
        userErrors { field message }
      }
    }
    """
    return {
        "query": query,
        "variables": {
            "id": collection_gid,
            "moves": moves
        }
    }

def main():
    df = pd.read_csv(CSV_PATH)

    # Nettoyage types numeriques
    df["produit_en_ligne_stock_actuel"] = pd.to_numeric(df["produit_en_ligne_stock_actuel"], errors="coerce").fillna(0).astype(int)
    df["quantite_vendue"] = pd.to_numeric(df["quantite_vendue"], errors="coerce").fillna(0).astype(int)

    # Nettoyage types date
    df["produit_en_ligne_ddm"] = pd.to_datetime(df["produit_en_ligne_ddm"], errors="coerce", format="%d/%m/%Y").dt.date
    df["Date première vente visible"] = pd.to_datetime(df["Date première vente visible"], errors="coerce", format="%d/%m/%Y").dt.date

    today = date.today()

    # Calcule le score merchandising
    df["score"] = df.apply(lambda r: compute_score(r, today), axis=1)
    df_sorted = df.sort_values(by=["score", "quantite_vendue"], ascending=[False, True])

    # Génére moves pour TOP_N produits a replacer
    moves = []
    for new_pos, (_, row) in enumerate(df_sorted.head(TOP_N).iterrows()):
        shopify_id_raw = row["∞ Shopify Id"]

        # check format pour requête
        if isinstance(shopify_id_raw, str) and shopify_id_raw.startswith("gid://"):
            product_gid = shopify_id_raw
        else:
            product_gid = f"gid://shopify/Product/{int(shopify_id_raw)}"

        moves.append({
            "id": product_gid,
            "newPosition": new_pos
        })

    payload = make_shopify_payload(COLLECTION_GID, moves)


    # format a envoyer a Shopify
    df_sorted[[
        "produit_en_ligne_nom_du_produit",
        "produit_en_ligne_stock_actuel",
        "quantite_vendue",
        "produit_en_ligne_ddm",
        "score",
        "∞ Shopify Id"
    ]].head(PREVIEW_NUMBER).to_csv(f"preview_top{PREVIEW_NUMBER}.csv", index=False)

    # preview des produits a replacer
    with open("payload.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print("OK ✅")
    print(f"- preview_top{PREVIEW_NUMBER}.csv généré (pour vérifier le tri)")
    print("- payload.json généré (prêt à envoyer à Shopify GraphQL)")

    return 0


if __name__ == "__main__":
    main()