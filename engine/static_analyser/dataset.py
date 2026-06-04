"""
Jeux de données et usine pour l'entraînement des modèles PyTorch.

Ce module fournit les classes nécessaires à la construction des jeux de données
d'entraînement pour les modèles d'analyse statique. Il inclut la classe de base
`BaseDataSet` ainsi que les implémentations concrètes pour chaque source de
données, et l'usine `DatasetFactory` pour les instancier.

Classes
-------
TrainingSource: Énumération des sources de données d'entraînement disponibles.
BaseDataSet: Classe de base abstraite pour les jeux de données PyTorch.
BugsInPyDataset: Jeu de données basé sur des fichiers Python avec bugs.
BanditDataset: Jeu de données basé sur des fichiers Python analysés par Bandit.
SyntaxNodeDataset: Jeu de données basé sur des projets SyntaxNode JSON.
DatasetFactory: Usine instanciant le bon jeu de données selon la source.
"""

from __future__ import annotations

from typing import Self, List, Any, Tuple, override, Dict, Optional
from enum import Enum, auto
from abc import ABC, abstractmethod
from pathlib import Path
import json
import ast

import torch
from torch.utils.data import Dataset, DataLoader
from torch.nn.utils import rnn

from ..ast_utils import ASTFlattener, ASTDirector, BuilderFactory, ImportFromExtractor

TRAINING_DATA_PATH = Path(__file__).parent.parent.parent / "ai_data" / "training_data"
DATASETS_PATH = Path(__file__).parent.parent.parent / "ai_data" / "datasets"
LEXICAL_FILE = TRAINING_DATA_PATH / "data.json"


class TrainingSource(Enum):
    """
    Énumération des sources de données d'entraînement disponibles.

    Attributes:
        BUGS_IN_PY: Fichiers Python contenant des bugs structurels.
        BANDIT: Fichiers Python avec du code potentiellement malveillant
            identifié par l'outil Bandit.
        SYNTAX_NODE_ERROR: Projets SyntaxNode JSON contenant des erreurs
            structurelles.
        SYNTAX_NODE_MALICIOUS: Projets SyntaxNode JSON contenant du code
            potentiellement malveillant.
    """
    BUGS_IN_PY = auto()
    BANDIT = auto()
    SYNTAX_NODE_ERROR = auto()
    SYNTAX_NODE_MALICIOUS = auto()


class BaseDataSet(Dataset, ABC):
    """
    Classe de base abstraite pour les jeux de données d'entraînement PyTorch.

    Gère la construction et la persistance du lexique partagé entre tous les
    jeux de données, la conversion des AST aplatis en tenseurs et l'interface
    `Dataset` de PyTorch.

    Attributes:
        _lexical (Dict[str, int]): Le lexique partagé associant chaque token
            à un indice entier.
        _max_len (int): La longueur maximale des séquences observées dans
            tous les jeux de données construits.
        _flattener (ASTFlattener): L'utilitaire de sérialisation d'AST
            partagé entre toutes les instances.
    """
    _lexical: Dict[str, int] = {}
    _max_len: int = 0
    _flattener: ASTFlattener = ASTFlattener()

    def __init__(self: Self, paths: List[Tuple[str, bool]]) -> None:
        """
        Initialise le jeu de données et construit le lexique.

        Charge le lexique depuis le disque si disponible, puis parcourt
        l'ensemble des fichiers pour enrichir le lexique et mettre à jour
        la longueur maximale des séquences.

        Args:
            paths (List[Tuple[str, bool]]): Une liste de tuples (chemin_fichier,
                expected_value) où expected_value indique si le fichier est
                considéré sûr (True) ou non (False).
        """
        if not BaseDataSet._lexical:
            self.load()
        self._paths: List[Tuple[str, bool]] = paths
        self._import_list: List[str] = []
        self._build_lexical()

    def __len__(self: Self) -> int:
        """
        Retourne le nombre d'échantillons dans le jeu de données.

        Returns:
            int: Le nombre de fichiers dans le jeu de données.
        """
        return len(self._paths)

    def __getitem__(self: Self, index: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Retourne l'échantillon à l'indice spécifié sous forme de tenseurs.

        Args:
            index (int): L'indice de l'échantillon à récupérer.

        Returns:
            Tuple[torch.Tensor, torch.Tensor]: Un tuple (données, étiquette) où
                données est un tenseur de forme `(max_len, 2)` et étiquette est
                un scalaire float (0.0 ou 1.0).
        """
        path, expected_value = self._paths[index]
        flatten_tree = self._transform_data(path)
        return self._data_into_tensor(flatten_tree, expected_value)

    def reset(self: Self) -> None:
        """
        Réinitialise le lexique partagé et la longueur maximale.

        À utiliser avant de reconstruire un lexique depuis zéro.
        """
        BaseDataSet._lexical = {}
        BaseDataSet._max_len = 0

    def save(self: Self) -> None:
        """
        Sauvegarde le lexique et la longueur maximale sur disque.

        Écrit le fichier `data.json` dans le répertoire des données d'entraînement
        pour permettre le chargement du lexique lors des sessions suivantes.
        """
        with open(LEXICAL_FILE, "w", encoding="utf-8") as f:
            content = {"lexical": self._lexical, "max_len": BaseDataSet._max_len}
            json.dump(content, f)

    @classmethod
    def load(cls) -> None:
        """
        Charge le lexique et la longueur maximale depuis le disque.

        Si le fichier n'existe pas, initialise le lexique avec les tokens
        réservés par défaut (PAD, Unknown, USER_*, No_value).
        """
        try:
            with open(LEXICAL_FILE, "r", encoding="utf-8") as f:
                content = json.load(f)
                cls._lexical = content.get("lexical", {})
                cls._max_len = content.get("max_len", 0)
        except FileNotFoundError:
            cls._lexical = {}
            cls._max_len = 0

        if not BaseDataSet._lexical:
            cls._lexical = {"PAD": 0, "Unknown": 1, "USER_str": 2, "USER_int": 3, "USER_float": 4, "USER_bool": 5, "USER_none": 6, "No_value": 7}

    def _build_lexical(self: Self) -> None:
        """
        Parcourt tous les fichiers du jeu de données pour enrichir le lexique.

        Met à jour `_max_len` avec la longueur maximale des séquences rencontrées
        et enrichit `_lexical` avec les nouveaux tokens, puis sauvegarde sur disque.
        """
        for (path, _) in self._paths:
            flatten_tree = self._transform_data(path)
            BaseDataSet._max_len = max(BaseDataSet._max_len, len(flatten_tree))
            for node in flatten_tree:
                word, _, _, _ = node
                if word not in BaseDataSet._lexical:
                    BaseDataSet._lexical[word] = len(BaseDataSet._lexical)

            for import_from in self._import_list:
                if import_from not in self._lexical:
                    self._lexical[import_from] = len(self._lexical)
            self._import_list.clear()

        self.save()

    @classmethod
    def _data_into_tensor(cls, flatten_tree: List[List[Any]], expected_value: bool) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Convertit une séquence de nœuds aplatis en tenseurs PyTorch.

        Encode chaque nœud (type, valeur) en indices du lexique, complète
        la séquence par du padding jusqu'à `_max_len` et retourne les
        tenseurs de données et d'étiquette.

        Args:
            flatten_tree (List[List[Any]]): La séquence aplatie de nœuds AST.
            expected_value (bool): L'étiquette de classification de la séquence
                (True = sûr, False = non sûr).

        Returns:
            Tuple[torch.Tensor, torch.Tensor]: Un tuple (données, étiquette) où
                données est de forme `(max_len, 2)` et étiquette est un scalaire float.
        """
        user_input = {None: "USER_none", "": "No_value", "str": "USER_str", "int": "USER_int", "float": "USER_float", "bool": "USER_bool"}
        main_list = []
        for node in flatten_tree:
            word, _, _, value = node
            word, value = BaseDataSet._lexical.get(word, 1), BaseDataSet._lexical.get(value, value)

            if value not in BaseDataSet._lexical:
                value = user_input.get(value, user_input.get(value.__class__.__name__, "Unknown"))
                value = BaseDataSet._lexical[value]

            main_list.append([word, value])

        while len(main_list) < BaseDataSet._max_len:
            main_list.append([0, 0])

        data_tensor = torch.tensor(main_list, dtype=torch.long)
        value_tensor = torch.tensor(expected_value, dtype=torch.float)

        return data_tensor, value_tensor

    @abstractmethod
    def _transform_data(self: Self, path: str) -> List[List[Any]]:
        """
        Transforme un fichier en séquence aplatie de nœuds AST.

        Méthode abstraite à implémenter par chaque sous-classe selon la
        nature de ses données (fichier Python, projet JSON SyntaxNode, etc.).

        Args:
            path (str): Le chemin vers le fichier à transformer.

        Returns:
            List[List[Any]]: La séquence aplatie de nœuds AST correspondant
                au fichier.
        """
        pass


class BugsInPyDataset(BaseDataSet):
    """
    Jeu de données basé sur des fichiers Python contenant des bugs structurels.

    Placeholder pour une future implémentation de la transformation des
    fichiers Python bugués.
    """

    def __init__(self: Self, paths: List[Tuple[str, bool]]) -> None:
        """
        Initialise le jeu de données avec les chemins des fichiers Python.

        Args:
            paths (List[Tuple[str, bool]]): Une liste de tuples (chemin_fichier,
                expected_value) vers les fichiers Python d'entraînement.
        """
        super().__init__(paths)


class BanditDataset(BaseDataSet):
    """
    Jeu de données basé sur des fichiers Python analysés par Bandit.

    Chaque fichier est parsé en AST Python, aplati et encodé comme
    séquence pour la classification de code potentiellement malveillant.
    """

    def __init__(self: Self, paths: List[Tuple[str, bool]]) -> None:
        """
        Initialise le jeu de données avec les chemins des fichiers Python.

        Args:
            paths (List[Tuple[str, bool]]): Une liste de tuples (chemin_fichier,
                expected_value) vers les fichiers Python d'entraînement.
        """
        super().__init__(paths)

    @override
    def _transform_data(self: Self, path: str) -> List[List[Any]]:
        """
        Parse un fichier Python et retourne son AST aplati.

        Args:
            path (str): Le chemin vers le fichier Python à transformer.

        Returns:
            List[List[Any]]: La séquence aplatie de nœuds AST du fichier Python.
        """
        with open(path) as f:
            tree = ast.parse(f.read())
        return BaseDataSet._flattener.flatten(tree)


class SyntaxNodeDataset(BaseDataSet):
    """
    Jeu de données basé sur des projets SyntaxNode au format JSON.

    Charge des projets JSON SyntaxNode, les convertit en AST Python via
    l'`ASTDirector`, les aplatit et extrait les imports pour enrichir le
    lexique.

    Attributes:
        _director (ASTDirector): Le directeur utilisé pour générer l'AST
            depuis les données JSON.
        _metadata (Dict[str, Any]): Les métadonnées de la bibliothèque
            graphique cible.
        _import_extractor (ImportFromExtractor): Le visiteur d'imports utilisé
            pour enrichir le lexique avec les noms importés.
    """

    def __init__(self: Self, paths: List[Tuple[str, bool]], library: str, metadata: Dict[str, Any]) -> None:
        """
        Initialise le jeu de données avec les chemins, la bibliothèque et les métadonnées.

        Args:
            paths (List[Tuple[str, bool]]): Une liste de tuples (chemin_fichier,
                expected_value) vers les projets JSON d'entraînement.
            library (str): Le nom de la bibliothèque graphique cible (ex: 'qt').
            metadata (Dict[str, Any]): Les métadonnées de la bibliothèque
                graphique.
        """
        self._director = ASTDirector(BuilderFactory.get_builder(library))
        self._metadata = metadata
        self._import_extractor = ImportFromExtractor()
        super().__init__(paths)

    @override
    def _transform_data(self: Self, path: str) -> List[List[Any]]:
        """
        Charge un projet JSON SyntaxNode et retourne son AST aplati.

        Args:
            path (str): Le chemin vers le fichier JSON du projet SyntaxNode.

        Returns:
            List[List[Any]]: La séquence aplatie de nœuds AST du projet.
        """
        with open(path, encoding="utf-8") as f:
            content = json.load(f)
        tree = self._director.make(content, self._metadata)
        self._import_extractor.visit(tree)
        return BaseDataSet._flattener.flatten(tree)


class DatasetFactory():
    """
    Usine instanciant le bon jeu de données selon la source d'entraînement.

    Centralise la création des jeux de données en associant chaque
    `TrainingSource` à sa classe concrète et en trouvant automatiquement
    les chemins des fichiers d'entraînement sur disque.

    Attributes:
        _sources (Dict[TrainingSource, type]): Registre des classes de jeux
            de données, indexé par source d'entraînement.
    """

    _sources: Dict[TrainingSource, type] = {
        TrainingSource.BUGS_IN_PY: BugsInPyDataset,
        TrainingSource.BANDIT: BanditDataset,
        TrainingSource.SYNTAX_NODE_ERROR: SyntaxNodeDataset,
        TrainingSource.SYNTAX_NODE_MALICIOUS: SyntaxNodeDataset
    }

    @staticmethod
    def create(training_source: TrainingSource, library: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> BaseDataSet:
        """
        Instancie et retourne le jeu de données correspondant à la source.

        Args:
            training_source (TrainingSource): La source de données à utiliser.
            library (Optional[str]): Le nom de la bibliothèque graphique cible,
                requis pour les sources SyntaxNode.
            metadata (Optional[Dict[str, Any]]): Les métadonnées de la bibliothèque
                graphique, requises pour les sources SyntaxNode.

        Returns:
            BaseDataSet: Une instance du jeu de données correspondant à la source,
                initialisée avec les chemins trouvés sur disque.
        """
        paths = DatasetFactory._find_paths(training_source)
        if library is None and metadata is None:
            return DatasetFactory._sources[training_source](paths)
        else:
            return DatasetFactory._sources[training_source](paths, library, metadata)

    @staticmethod
    def _find_paths(training_source: TrainingSource) -> List[Tuple[str, bool]]:
        """
        Trouve et retourne les chemins des fichiers d'entraînement sur disque.

        Cherche les fichiers dans les sous-dossiers 'clean' (étiquette True)
        et 'unclean' (étiquette False) du répertoire correspondant à la source.

        Args:
            training_source (TrainingSource): La source de données dont les
                fichiers sont à trouver.

        Returns:
            List[Tuple[str, bool]]: Une liste de tuples (chemin_fichier, étiquette)
                pour tous les fichiers trouvés.
        """
        path_list = []
        folder = training_source.name.lower()
        clean_path = DATASETS_PATH / folder / "clean"
        unclean_path = DATASETS_PATH / folder / "unclean"
        for p in clean_path.iterdir():
            path_list.append((str(p), True))
        for p in unclean_path.iterdir():
            path_list.append((str(p), False))
        return path_list
