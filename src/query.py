"""
ETAPES 4 & 5 : Vectoriser la question de l'utilisateur, puis chercher
les chunks les plus proches par similarite cosinus.

On code la similarite cosinus A LA MAIN ici (au lieu d'utiliser une
fonction toute faite de sklearn) pour bien voir la formule exacte
qu'on a vue en theorie : l'angle entre deux vecteurs.
"""

import pickle
import sys
from pathlib import Path

import numpy as np

PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"


def cosine_similarity(vec_a, vec_b) -> float:
    """La formule exacte de la similarite cosinus :

        cos(angle) = (A . B) / (||A|| * ||B||)

    - A . B       : le produit scalaire (on multiplie les composantes une a
                    une puis on additionne tout)
    - ||A||, ||B|| : la "longueur" de chaque vecteur (norme)

    Resultat entre -1 (oppose) et 1 (identique en direction), exactement
    comme dans nos exemples avec l'ecran noir, le mot de passe et l'imprimante.
    """
    vec_a = np.asarray(vec_a.todense()).flatten()
    vec_b = np.asarray(vec_b.todense()).flatten()

    dot_product = np.dot(vec_a, vec_b)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


def search(question: str, top_k: int = 3) -> list[dict]:
    store_path = PROCESSED_DIR / "vector_store.pkl"
    with open(store_path, "rb") as f:
        store = pickle.load(f)

    vectorizer = store["vectorizer"]
    chunk_vectors = store["vectors"]
    chunks = store["chunks"]

    # Etape 4 : on vectorise la question avec le MEME vectorizer que les chunks
    question_vector = vectorizer.transform([question])

    # Etape 5 : on compare la question a CHAQUE chunk stocke, un par un
    scores = []
    for i in range(chunk_vectors.shape[0]):
        chunk_vector = chunk_vectors[i]
        similarity = cosine_similarity(question_vector, chunk_vector)
        scores.append((similarity, chunks[i]))

    # On trie du score le plus haut au plus bas, et on garde les meilleurs
    scores.sort(key=lambda x: x[0], reverse=True)
    top_results = scores[:top_k]

    return [{"score": round(score, 4), "chunk": chunk} for score, chunk in top_results]


def main():
    question = sys.argv[1] if len(sys.argv) > 1 else "mon ecran reste noir au demarrage"

    print(f"Question : {question}\n")
    results = search(question, top_k=3)

    for rank, r in enumerate(results, start=1):
        print(f"#{rank} - score de similarite : {r['score']}")
        print(f"    Section : {r['chunk']['metadata']['section']}")
        print(f"    Extrait : {r['chunk']['text'][:100]}...")
        print()


if __name__ == "__main__":
    main()
