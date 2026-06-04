# SyntaxNode — Moteur de génération de code

> **Contribution personnelle** au projet d'équipe [SyntaxNode](https://www.syntaxnode.ca) — une application web permettant de concevoir graphiquement des interfaces Qt et d'en générer le code Python automatiquement.
>
> 🌐 **Site en ligne : [www.syntaxnode.ca](https://www.syntaxnode.ca)**
>
> Ce dépôt contient exclusivement le **moteur backend** dont j'étais responsable : le pipeline complet de validation, de construction d'AST, d'analyse statique par réseau de neurones et de génération de code.

---

## Aperçu

À partir d'un schéma nodal JSON produit par l'éditeur visuel, le moteur :

1. **Valide** la structure JSON avec des modèles Pydantic
2. **Construit** un arbre syntaxique abstrait (AST) représentant l'interface Qt
3. **Analyse** le code utilisateur avec deux modèles PyTorch (détection d'erreurs et de code malveillant)
4. **Génère** le code Python PySide6 correspondant
5. **Compresse** les fichiers dans une archive ZIP téléchargeable
6. **Produit** une image de prévisualisation de l'interface en cours de conception

## Démonstration

https://github.com/user-attachments/assets/02c60795-dddd-42aa-b768-83e7ac58fe6f

https://github.com/user-attachments/assets/a64eb788-1b13-4076-9b0e-7c71765d7c1b

---

## Fonctionnalités principales

- **Génération de code Python/PySide6** à partir d'un graphe de composants Qt
- **Introspection Qt dynamique** via `QMetaObject` — extraction des propriétés, signaux, slots, énumérations et types C++ complexes au moment de l'exécution
- **Génération d'images de prévisualisation** — rendu bitmap d'un composant ou de l'interface complète, ciblé par identifiant de nœud
- **Analyse statique par apprentissage automatique** — deux modèles GRU (PyTorch) détectent les erreurs structurelles et les fonctions potentiellement malveillantes
- **Validation en deux passes** — JSON (Pydantic) puis AST (visiteurs)
- **Gestion d'erreurs structurée** — chaque erreur porte un identifiant de nœud (`focus_id`) permettant à l'interface de surligner le composant problématique
- **Architecture extensible** — patterns Factory, Strategy et Director facilitent l'ajout de nouveaux langages ou bibliothèques cibles

---

## Architecture

```
engine/
├── core.py                  # Point d'entrée principal (SyntaxNodeEngine)
├── config/                  # Configuration abstraite et profils (Default, Extended, Test)
├── adapters/                # Extraction de métadonnées Qt via QMetaObject
├── ast_utils/               # Construction de l'AST (Director, Factory, Builder, Flattener)
├── strategies/              # Stratégies de génération par langage/bibliothèque
├── generator/               # Génération du code source et compression ZIP
├── static_analyser/         # Modèles PyTorch et datasets pour l'analyse statique
├── validators/              # Validation JSON (Pydantic) et validation de l'AST
├── visitors/                # Visiteurs AST (collecte de données pour les modèles ML)
├── utils/                   # Sérialiseur, organisateur de code, utilitaires
└── error.py                 # Hiérarchie d'exceptions personnalisées
```

### Flux de données

```
JSON (schéma nodal)
    │
    ▼
[1] validators/vjson.py      — Validation Pydantic du schéma
    │
    ▼
[2] ast_utils/director.py    — Orchestration de la construction de l'AST
    │   ast_utils/factory.py — Sélection du bon builder selon le type de nœud
    │   adapters/qt_adapter.py — Introspection des composants Qt
    │
    ▼
[3] static_analyser/         — Analyse des fonctions utilisateur (modèles GRU)
    │
    ▼
[4] strategies/python_strategy.py — Parcours de l'AST et génération du code
    │   generator/code_generator.py
    │
    ▼
[5] Archive ZIP (BytesIO)
```

---

## Technologies

| Catégorie | Outils |
|---|---|
| Langage | Python 3.12+ |
| Interface Qt | PySide6 6.10+ |
| Apprentissage automatique | PyTorch (GRU, embeddings) |
| Validation de données | Pydantic 2.x |
| Backend web | Django 6.x, Django REST Framework |
| Typage | Type hints complets (typing, Self) |

---

## Installation

```bash
# Cloner le dépôt
git clone https://github.com/laframboisemario19/SyntaxNode_Engine.git
cd SyntaxNode_Engine

# Créer un environnement virtuel
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/macOS

# Installer les dépendances
pip install -r requirements.txt
```

---

## Utilisation

```python
from engine import SyntaxNodeEngine, PredictionValue
from engine.strategies import ConfigType

engine = SyntaxNodeEngine()
engine.set_language("python")
engine.set_lib("qt", ConfigType.DEFAULT)

# Générer le code (retourne un BytesIO contenant l'archive ZIP)
with open("mon_projet.json") as f:
    data = json.load(f)

zip_buffer = engine.get_code_files(data)

# Valider un schéma sans générer de code
is_valid, errors = engine.validate_data(data)

# Générer une image de prévisualisation d'un composant
bitmap = engine.generate_bitmap(data, target_id="node_id")
```

### Format d'entrée (JSON)

```json
[{
  "id_project": "uuid",
  "project_name": "MonApplication",
  "components": [
    {
      "id": "node_uuid",
      "type": "QMainWindow",
      "category": "widget",
      "position": { "x": 0.0, "y": 0.0 },
      "name": "fenetre_principale",
      "inheritance": [{"type": "QMainWindow", "module": "PySide6.QtWidgets"}],
      "properties": [
        {"name": "windowTitle", "type": "str", "value": "MonApp"}
      ],
      "child": ["uuid_enfant_1"]
    }
  ],
  "links": [
    {"source": "uuid_signal", "target": "uuid_slot", "type": "signal_slot"}
  ]
}]
```

---

## Analyse statique par apprentissage automatique

Deux modèles GRU analysent l'AST aplati des fonctions écrites par l'utilisateur :

| Modèle | Rôle | Seuil de détection |
|---|---|---|
| `sn_error.pt` | Détecte les erreurs structurelles dans le code généré | — |
| `bandit.pt` | Détecte les fonctions potentiellement malveillantes | Score ≥ 0.4 |

L'inférence fonctionne avec les modèles pré-entraînés inclus (fichiers `.pt`). Le pipeline d'entraînement est en développement actif.

---

## Gestion des erreurs

Toutes les exceptions héritent de `SyntaxNodeError` et transportent deux messages distincts : un message utilisateur (affiché dans l'interface) et un message développeur (journalisé côté serveur).

| Exception | Déclenchée quand |
|---|---|
| `LinksError` | Connexion invalide ou dépendance circulaire détectée |
| `QtStructureError` | La hiérarchie des widgets Qt viole les règles structurelles |
| `CodeReferenceError` | Le code utilisateur référence une variable ou fonction inconnue |
| `IllegalImportError` | Un module requis par un composant ne peut pas être importé |
| `FatalError` | Une fonction potentiellement malveillante est détectée |
