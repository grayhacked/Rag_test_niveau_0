"""
ETAPE 3 : Vectorisation + stockage (notre "base de donnees vectorielle" maison)

On transforme chaque chunk de texte en vecteur grace a TF-IDF (Term
Frequency - Inverse Document Frequency), une methode d'embedding simple
qui ne necessite pas de telecharger un gros modele depuis internet.

Le principe TF-IDF en une phrase : chaque mot du vocabulaire devient une
dimension du vecteur, et sa valeur est haute si le mot est frequent dans
CE chunk mais rare dans les AUTRES chunks (donc "discriminant").

C'est plus simple qu'un vrai modele d'embedding de reseau de neurones,
mais la suite du pipeline (stockage, similarite cosinus, recherche) est
EXACTEMENT la meme mecanique qu'avec un embedding plus sophistique.
"""

import json
import pickle
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer

PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"


def main():
    chunks_path = PROCESSED_DIR / "chunks.json"
    chunks = json.loads(chunks_path.read_text(encoding="utf-8"))

    texts = [c["text"] for c in chunks]

    # Le vectorizer apprend le vocabulaire de tous les chunks, puis transforme
    # chaque texte en un vecteur. C'est l'equivalent de notre "modele d'embedding".
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(texts)  # matrice (nb_chunks x taille_vocabulaire)

    print(f"Vocabulaire appris : {len(vectorizer.vocabulary_)} mots uniques")
    print(f"Chaque chunk est maintenant un vecteur de dimension {vectors.shape[1]}")

    # On sauvegarde : le vectorizer (pour pouvoir vectoriser une future question),
    # les vecteurs de chaque chunk, et les chunks eux-memes (texte + metadonnees).
    # C'est notre "base de donnees vectorielle" - dans un vrai projet ce serait
    # Chroma ou Pinecone, mais le principe de stockage est le meme : vecteur + donnees.
    store = {
        "vectorizer": vectorizer,
        "vectors": vectors,
        "chunks": chunks,
    }
    store_path = PROCESSED_DIR / "vector_store.pkl"
    with open(store_path, "wb") as f:
        pickle.dump(store, f)

    print(f"\nBase vectorielle sauvegardee dans {store_path}")


if __name__ == "__main__":
    main()
