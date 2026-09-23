"""
ETAPE 6 : Generation de la reponse finale (le "sandwich")

On assemble trois blocs de texte :
  1. L'instruction systeme (comment le modele doit se comporter)
  2. Le contexte recupere (les chunks trouves par query.py)
  3. La question de l'utilisateur

... et on envoie ce sandwich complet au modele de langage, qui lit tout
ca comme un seul texte et genere la reponse la plus logique, ancree dans
le contexte fourni.

Pour appeler un vrai modele, il vous faut une cle API. Sur votre poste :
    pip install openai
    export OPENAI_API_KEY="votre_cle_ici"
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent))
from query import search

SYSTEM_INSTRUCTION = """Tu es l'assistant de support niveau 1 interne de l'entreprise.
Reponds a la question de l'employe UNIQUEMENT en te basant sur le contexte
fourni ci-dessous, extrait de notre documentation officielle.
Si le contexte ne contient pas la reponse, dis clairement que tu ne sais
pas et propose de creer un ticket pour le support niveau 2.
Sois concis et donne des etapes actionnables."""


def build_prompt(question: str, top_k: int = 3) -> tuple[str, str]:
    """Construit le sandwich : recupere les chunks pertinents, puis assemble
    le contexte avec la question. Retourne (system, user_message)."""
    results = search(question, top_k=top_k)

    context_blocks = []
    for r in results:
        section = r["chunk"]["metadata"]["section"]
        text = r["chunk"]["text"]
        context_blocks.append(f"[Extrait - {section}]\n{text}")

    context = "\n\n".join(context_blocks)

    user_message = f"""Contexte extrait de la documentation :

{context}

---

Question de l'employe : {question}"""

    return SYSTEM_INSTRUCTION, user_message


def generate_answer(question: str) -> str:
    system, user_message = build_prompt(question)

    api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("=" * 70)
        print("PAS DE CLE API DETECTEE - voici le sandwich qui SERAIT envoye")
        print("au modele (chez vous, avec une cle API, ceci generera une")
        print("vraie reponse automatiquement) :")
        print("=" * 70)
        print(f"\n--- SYSTEM ---\n{system}")
        print(f"\n--- USER MESSAGE ---\n{user_message}")
        print("\n" + "=" * 70)
        return "(pas de reponse generee - cle API manquante, voir ci-dessus)"

    # Avec une cle API, voici l'appel reel :
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        max_tokens=500,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    question = sys.argv[1] if len(sys.argv) > 1 else "mon ecran reste noir au demarrage"
    print(f"QUESTION : {question}\n")
    answer = generate_answer(question)
    print(f"\nREPONSE : {answer}")
