# Support RAG - Prototype

Assistant de support niveau 1 base sur RAG (Retrieval-Augmented Generation).
Prototype construit pour prouver la valeur du concept avant une version production.

## Le pipeline, en 4 scripts = 6 etapes

```
data/raw/*.txt          <- vos documents bruts (procedures de support)
      |
      v
  1&2. src/ingest.py       -> extraction + decoupage en chunks
      |
      v
data/processed/chunks.json
      |
      v
  3.   src/embed_store.py  -> vectorisation (TF-IDF) + stockage
      |
      v
data/processed/vector_store.pkl
      |
      v
  4&5. src/query.py        -> vectorise la question + recherche par
                               similarite cosinus (codee a la main)
      |
      v
  6.   src/generate.py     -> assemble le "sandwich" (instruction +
                               contexte + question) et appelle le
                               modele de langage
```

## Installation

```bash
pip install scikit-learn numpy anthropic
export ANTHROPIC_API_KEY="votre_cle_ici"
```

## Faire tourner le pipeline complet

```bash
# 1. Ajoutez vos vrais documents dans data/raw/ (format .txt pour l'instant,
#    utilisez PyPDF2 ou pdfplumber pour extraire depuis un PDF en amont)

# 2. Extraction + decoupage
python3 src/ingest.py

# 3. Vectorisation + stockage
python3 src/embed_store.py

# 4. Test de recherche seule (optionnel, pour debugger)
python3 src/query.py "votre question ici"

# 5. Generation de la reponse complete
python3 src/generate.py "votre question ici"
```

## Limites de ce prototype (a corriger avant la production)

- **Embedding TF-IDF** : simple et local, mais moins performant qu'un vrai
  modele d'embedding (sentence-transformers, ou l'API d'un modele comme
  Claude). A remplacer pour de meilleurs resultats semantiques.
- **Chunking par section `== Titre ==`** : fonctionne pour nos documents
  bien structures, mais un vrai PDF n'a pas forcement ce format. Utiliser
  un chunking par paragraphes/taille fixe avec chevauchement (overlap) en
  pratique.
- **Stockage en fichier .pkl** : suffisant pour un prototype avec quelques
  documents. Pour des milliers de documents, passer a une vraie base
  vectorielle comme Chroma ou Pinecone.
- **Pas encore d'agent** : ce prototype repond a des questions, il n'agit
  pas encore (pas de creation automatique de ticket, pas de reinitialisation
  de mot de passe). C'est la prochaine etape.
- **Confidentialite** : verifiez qu'aucune donnee client sensible n'est
  envoyee a une API externe sans anonymisation prealable.

## Prochaine etape : la couche agent

Donner au modele acces a des outils (creer_ticket, reinitialiser_mdp) via
le "function calling" de l'API Anthropic, et une boucle qui laisse le
modele decider s'il repond ou s'il agit.
