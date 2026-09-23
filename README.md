# Support RAG - Prototype

Assistant de support niveau 1 base sur le principe **RAG** (*Retrieval-Augmented
Generation*). Le prototype recherche les passages les plus proches d'une
question dans une documentation locale, puis peut transmettre ces passages a
un modele OpenAI pour generer une reponse ancree dans le contexte.

## Fonctionnement

```text
data/raw/*.txt
    |  src/ingest.py : lecture et decoupage par sections == Titre ==
    v
data/processed/chunks.json
    |  src/embed_store.py : vectorisation TF-IDF et sauvegarde
    v
data/processed/vector_store.pkl
    |  src/query.py : recherche par similarite cosinus
    v
src/generate.py : contexte + question -> reponse du modele
```

Le stockage est volontairement local et simple : les embeddings sont des
vecteurs TF-IDF et le fichier `vector_store.pkl` contient le vectorizer, les
vecteurs et les metadonnees des chunks.

## Prerequis

- Python 3.10 ou plus recent
- Une invite de commande PowerShell ou un terminal integre VS Code
- Une cle API OpenAI uniquement pour l'etape de generation

## Installation sous Windows

Depuis la racine du projet :

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Si PowerShell bloque l'activation dans la session courante :

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

Dans VS Code, selectionnez ensuite `.venv\Scripts\python.exe` avec
**Python: Select Interpreter**.

## Configuration

Copiez le modele de configuration dans un fichier `.env` a la racine, puis
renseignez vos valeurs :

```dotenv
APP_ENV=development
LLM_API_KEY=votre_cle_api
LLM_MODEL=gpt-4o-mini
```

`.env` est ignore par Git. Ne committez jamais une cle API et ne la partagez
pas dans une capture, un ticket ou une conversation. Si une cle a ete exposee,
revoquez-la immediatement et creez-en une nouvelle.

## Execution

Ajoutez ou modifiez les documents texte dans `data/raw/`. Les sections a
indexer doivent etre delimitees ainsi :

```text
== Probleme d'ecran noir ==
Redemarrez le poste et verifiez le cable video.
```

Puis executez les etapes dans cet ordre :

```powershell
python src/ingest.py
python src/embed_store.py
```

Testez uniquement la recherche :

```powershell
python src/query.py "mon ecran reste noir au demarrage"
```

Generez une reponse avec le modele configure :

```powershell
python src/generate.py "mon ecran reste noir au demarrage"
```

Sans `LLM_API_KEY`, `generate.py` affiche le prompt construit au lieu
d'appeler l'API. Cela permet de verifier la recuperation sans consommer de
quota.

## Structure du projet

```text
data/raw/                 Documents source .txt
data/processed/           Chunks et index generes localement
src/ingest.py             Extraction et decoupage
src/embed_store.py        Vectorisation TF-IDF
src/query.py              Recherche des chunks pertinents
src/generate.py           Generation de la reponse
requirements.txt          Dependances Python
```

Les fichiers `data/processed/chunks.json` et `data/processed/vector_store.pkl`
sont regeneres par le pipeline apres toute modification documentaire.

## Depannage

**`Import "openai" could not be resolved`**

Verifiez que VS Code utilise `.venv`, puis installez les dependances dans ce
meme interpreteur :

```powershell
python -m pip install -r requirements.txt
python -c "from openai import OpenAI; print('openai OK')"
```

**`FileNotFoundError` sur `vector_store.pkl`**

Executez d'abord `ingest.py`, puis `embed_store.py`.

**Aucun chunk ou resultats peu pertinents**

Verifiez que les fichiers sont en `.txt`, que les titres utilisent bien la
syntaxe `== Titre ==`, et que les termes de la question apparaissent dans la
documentation. TF-IDF ne comprend pas les synonymes comme un modele
semantique.

## Limites connues

- TF-IDF est rapide et local, mais moins semantique qu'un vrai modele
  d'embedding.
- Le decoupage depend de titres `== ... ==` et ne traite pas directement les
  PDF.
- Le fichier pickle convient a un prototype local, pas a un index partage ou
  volumineux.
- Le prototype repond aux questions mais ne declenche pas encore d'actions
  comme la creation d'un ticket.
- Les donnees sensibles doivent etre anonymisees avant tout envoi a une API
  externe.

## Evolutions envisagees

1. Ajouter une extraction PDF et un chunking avec taille maximale et overlap.
2. Remplacer TF-IDF par des embeddings semantiques et un vrai vector store.
3. Ajouter des tests automatises sur le parsing, la recherche et le prompt.
4. Encadrer les actions support avec des outils explicites et des controles
   avant execution.
