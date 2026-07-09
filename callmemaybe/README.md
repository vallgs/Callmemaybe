# CallMeMaybe / project by vallangl

A from-scratch implementation of **constrained decoding for function calling** with a small local LLM. Instead of asking the model to "please output valid JSON" and hoping for the best, the token generation loop itself masks out every token that would break the expected JSON grammar, so the model is *structurally* unable to hallucinate an invalid function call.

## How it works

1. A list of callable functions is described in a JSON schema (name, description, parameters, return type).
2. A small causal language model ([`Qwen/Qwen3-0.6B`](https://huggingface.co/Qwen/Qwen3-0.6B) by default) receives a prompt built from the available functions and a natural-language question (e.g. *"What is the sum of 2 and 3?"*).
3. Generation happens **token by token**. At each step:
   - the model produces raw logits for the next token,
   - a hand-written grammar validator ([`src/util.py`](src/util.py)) checks, for every token in the vocabulary, whether appending it to the text generated so far still leads to a valid `{"name": "...", "parameters": {...}}` object matching one of the known function signatures,
   - invalid tokens are masked to `-inf` before picking the arg-max token.
4. Generation stops as soon as a balanced, complete JSON object has been produced (or after a token budget is exhausted).
5. The resulting `{"name": ..., "parameters": ...}` object is parsed, numeric parameters are cast to `float`, and results are written to an output file.

This grammar validator is a small state machine that tracks, character by character, where we are in the JSON structure: the function name, the `"parameters": {` opening, each key (constrained to the target function's known parameter names), the `:` separator, string vs. number values, and the closing braces — always leaving only `,` or `}` open once every required parameter has been written.

## Project structure

```
src/
├── __main__.py          # CLI entrypoint: loads data, runs the generation loop, writes results
├── engine.py             # GenerationEngine: orchestrates logits -> mask -> arg-max per step
├── util.py                # Grammar/state-machine validator driving the token mask
├── models.py               # Pydantic models: FunctionDefinition, Parameter, PromptTest
├── loader.py                # JSON loading & validation for functions/tests
├── parsing/arg.py            # CLI argument parsing (--input, --output, --functions_definition)
└── llm_sdk/                   # Small_LLM_Model: thin wrapper around a HF transformers model
    └── llm_sdk/__init__.py     # encode/decode/get_logits_from_input_ids/vocab helpers

data/
├── input/
│   ├── functions_definition.json   # Available functions (schema)
│   └── function_calling_tests.json # Natural-language prompts to translate into calls
├── output/
│   └── function_calling_result.json # Generated function calls
└── correction/
    └── function_calling_corrections.json # Expected calls + expected outputs (grading)

moulinette/                # Standalone grading/exercise-generation CLI (used to check this project)
```

## Data format

**`functions_definition.json`** — the functions the model is allowed to call:

```json
{
  "name": "fn_add_numbers",
  "description": "Add two numbers together and return their sum.",
  "parameters": { "a": { "type": "number" }, "b": { "type": "number" } },
  "returns": { "type": "number" }
}
```

**`function_calling_tests.json`** — natural-language prompts to convert into a call:

```json
{ "prompt": "What is the sum of 2 and 3?" }
```

**Output** — one object per successfully parsed prompt:

```json
{
  "prompt": "What is the sum of 2 and 3?",
  "name": "fn_add_numbers",
  "parameters": { "a": 2.0, "b": 3.0 }
}
```

## Installation

Requires Python >= 3.10 and [`uv`](https://docs.astral.sh/uv/).

```bash
make install   # uv sync
```

## Usage

```bash
make run        # uv run python -m src
make debug      # same, under pdb
```

Custom paths can be passed directly:

```bash
uv run python -m src \
  --input data/input/function_calling_tests.json \
  --functions_definition data/input/functions_definition.json \
  --output data/output/function_calling_result.json
```

## Linting

```bash
make lint            # flake8 + mypy (warn-return-any, disallow-untyped-defs, ...)
make lint--strict     # same, with mypy --strict
```

`src/llm_sdk` and `moulinette` are excluded from linting (third-party/tooling code).

## Grading (`moulinette`)

The `moulinette/` folder is a separate CLI (`fire`-based) used to generate exercise sets and grade a student's `function_calling_result.json` against expected outputs by actually calling the reference functions and comparing results — not just comparing JSON text.

```bash
cd moulinette
uv run python -m moulinette prepare_exercises --set public
uv run python -m moulinette grade_student_answers <path_to_answers.json> --set public
```

---

# CallMeMaybe (Français)

Une implémentation *from scratch* du **décodage contraint (constrained decoding)** pour le function calling avec un petit LLM local. Plutôt que de demander gentiment au modèle de "générer du JSON valide" et d'espérer que ça marche, la boucle de génération de tokens masque elle-même tout token qui casserait la grammaire JSON attendue : le modèle est donc *structurellement* incapable d'halluciner un appel de fonction invalide.

## Fonctionnement

1. La liste des fonctions appelables est décrite dans un schéma JSON (nom, description, paramètres, type de retour).
2. Un petit modèle de langage causal ([`Qwen/Qwen3-0.6B`](https://huggingface.co/Qwen/Qwen3-0.6B) par défaut) reçoit un prompt construit à partir des fonctions disponibles et d'une question en langage naturel (ex : *"What is the sum of 2 and 3?"*).
3. La génération se fait **token par token**. À chaque étape :
   - le modèle produit les logits bruts pour le prochain token,
   - un validateur de grammaire écrit à la main ([`src/util.py`](src/util.py)) vérifie, pour chaque token du vocabulaire, si l'ajouter au texte déjà généré mène toujours à un objet `{"name": "...", "parameters": {...}}` valide correspondant à l'une des fonctions connues,
   - les tokens invalides sont masqués à `-inf` avant de sélectionner le token de score maximal.
4. La génération s'arrête dès qu'un objet JSON complet et équilibré (accolades ouvrantes/fermantes) a été produit, ou après épuisement d'un budget de tokens.
5. L'objet `{"name": ..., "parameters": ...}` obtenu est parsé, les paramètres numériques sont convertis en `float`, et les résultats sont écrits dans un fichier de sortie.

Ce validateur de grammaire est une petite machine à états qui suit, caractère par caractère, où l'on se trouve dans la structure JSON : le nom de la fonction, l'ouverture de `"parameters": {`, chaque clé (contrainte aux noms de paramètres connus de la fonction ciblée), le séparateur `:`, les valeurs de type chaîne ou nombre, et les accolades fermantes — en ne laissant ouvert que `,` ou `}` une fois que tous les paramètres requis ont été écrits.

## Structure du projet

```
src/
├── __main__.py          # Point d'entrée CLI : charge les données, lance la boucle de génération, écrit les résultats
├── engine.py             # GenerationEngine : orchestre logits -> masque -> arg-max à chaque étape
├── util.py                # Validateur de grammaire (machine à états) pilotant le masque de tokens
├── models.py               # Modèles Pydantic : FunctionDefinition, Parameter, PromptTest
├── loader.py                # Chargement & validation JSON des fonctions/tests
├── parsing/arg.py            # Parsing des arguments CLI (--input, --output, --functions_definition)
└── llm_sdk/                   # Small_LLM_Model : fine surcouche autour d'un modèle HF transformers
    └── llm_sdk/__init__.py     # Fonctions encode/decode/get_logits_from_input_ids/vocab

data/
├── input/
│   ├── functions_definition.json   # Fonctions disponibles (schéma)
│   └── function_calling_tests.json # Prompts en langage naturel à convertir en appels
├── output/
│   └── function_calling_result.json # Appels de fonction générés
└── correction/
    └── function_calling_corrections.json # Appels attendus + sorties attendues (correction)

moulinette/                # CLI autonome de génération d'exercices/correction (utilisée pour évaluer ce projet)
```

## Format des données

**`functions_definition.json`** — les fonctions que le modèle peut appeler :

```json
{
  "name": "fn_add_numbers",
  "description": "Add two numbers together and return their sum.",
  "parameters": { "a": { "type": "number" }, "b": { "type": "number" } },
  "returns": { "type": "number" }
}
```

**`function_calling_tests.json`** — prompts en langage naturel à convertir en appel :

```json
{ "prompt": "What is the sum of 2 and 3?" }
```

**Sortie** — un objet par prompt correctement parsé :

```json
{
  "prompt": "What is the sum of 2 and 3?",
  "name": "fn_add_numbers",
  "parameters": { "a": 2.0, "b": 3.0 }
}
```

## Installation

Nécessite Python >= 3.10 et [`uv`](https://docs.astral.sh/uv/).

```bash
make install   # uv sync
```

## Utilisation

```bash
make run        # uv run python -m src
make debug      # idem, sous pdb
```

Des chemins personnalisés peuvent être passés directement :

```bash
uv run python -m src \
  --input data/input/function_calling_tests.json \
  --functions_definition data/input/functions_definition.json \
  --output data/output/function_calling_result.json
```

## Linting

```bash
make lint            # flake8 + mypy (warn-return-any, disallow-untyped-defs, ...)
make lint--strict     # idem, avec mypy --strict
```

`src/llm_sdk` et `moulinette` sont exclus du linting (code tiers/outillage).

## Correction (`moulinette`)

Le dossier `moulinette/` est une CLI séparée (basée sur `fire`) utilisée pour générer des jeux d'exercices et corriger le fichier `function_calling_result.json` d'un étudiant en appelant réellement les fonctions de référence et en comparant les résultats — pas seulement en comparant du texte JSON.

```bash
cd moulinette
uv run python -m moulinette prepare_exercises --set public
uv run python -m moulinette grade_student_answers <chemin_vers_answers.json> --set public
```
