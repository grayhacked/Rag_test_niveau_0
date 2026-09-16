"""
ETAPE 1 & 2 : Extraction + Decoupage (chunking)

Ce script lit les documents bruts dans data/raw/, les decoupe en petits
morceaux coherents (un morceau = une section), et sauvegarde le resultat
dans data/processed/chunks.json avec leurs metadonnees (nom du fichier,
titre de section).

Pourquoi decouper par section (== Titre ==) plutot que par nombre de mots fixe ?
Parce qu'on veut que chaque morceau reste focalise sur UN SEUL sujet,
exactement comme on l'a vu : eviter le "marron dilue" en melangeant
plusieurs sujets dans un meme vecteur.
"""

import json
import re
from pathlib import Path

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"


def extract_text(filepath: Path) -> str:
    """Etape 1 : extraction du texte brut. Pour un vrai PDF, on utiliserait
    pypdf ou pdfplumber ici. Pour un .txt, on lit directement."""
    return filepath.read_text(encoding="utf-8")


def chunk_by_section(text: str, source_name: str) -> list[dict]:
    """Etape 2 : decoupage. On coupe a chaque titre de section (== ... ==).
    Chaque morceau garde une etiquette (metadonnee) qui dit d'ou il vient."""
    # On separe le texte a chaque titre de section
    pattern = r"==\s*(.+?)\s*=="
    parts = re.split(pattern, text)

    chunks = []
    # parts alterne : [texte_avant_premier_titre, titre1, contenu1, titre2, contenu2, ...]
    for i in range(1, len(parts), 2):
        title = parts[i].strip()
        content = parts[i + 1].strip() if i + 1 < len(parts) else ""
        if not content:
            continue
        chunks.append({
            "id": f"{source_name}::{title}",
            "text": content,
            "metadata": {
                "source": source_name,
                "section": title,
            },
        })
    return chunks


def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    all_chunks = []

    for filepath in RAW_DIR.glob("*.txt"):
        print(f"Extraction de {filepath.name}...")
        text = extract_text(filepath)
        chunks = chunk_by_section(text, filepath.stem)
        all_chunks.extend(chunks)
        print(f"  -> {len(chunks)} morceaux (chunks) crees")

    output_path = PROCESSED_DIR / "chunks.json"
    output_path.write_text(
        json.dumps(all_chunks, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nTotal : {len(all_chunks)} chunks sauvegardes dans {output_path}")


if __name__ == "__main__":
    main()
