"""
Implémentation de la stratégie de génération de code Python.

Ce module fournit la classe `PythonStrategy`, qui orchestre la génération
de code Python à partir du graphe nodal, ainsi que l'entraînement et
l'inférence des modèles PyTorch pour l'analyse statique du code utilisateur.

Classes
-------
PythonStrategy: Stratégie concrète de génération de code pour le langage Python.
"""

from typing import Self, Any, List, Dict
from pathlib import Path
from io import BytesIO

from .base import LanguageStrategy, ImageGeneratorStrategy
from ..ast_utils import BuilderFactory, ASTDirector, ASTFlattener
from ..generator import CodeGenerator
from ..static_analyser import DatasetFactory, TrainingSource, BaseDataSet, PyTorchModel

SN_ERROR_MODEL_PATH = Path(__file__).parent.parent.parent / "ai_data" / "model" / "sn_error.pt"
BANDIT_MODEL_PATH = Path(__file__).parent.parent.parent / "ai_data" / "model" / "bandit.pt"

class PythonStrategy(LanguageStrategy):
    """
    Stratégie concrète de génération de code pour le langage Python.

    Orchestre la création de l'AST, la génération de code source et le rendu
    visuel des composants. Gère également l'entraînement et l'inférence de
    deux modèles PyTorch : un pour la détection d'erreurs structurelles
    SyntaxNode et un pour la détection de code potentiellement malveillant
    (Bandit).

    Attributes:
        _name (str): Le nom du langage, toujours 'python'.
        _image_generator (ImageGeneratorStrategy): Le moteur de rendu visuel actif.
        _available_lib (list): Les bibliothèques graphiques disponibles.
        _directors (dict[str, ASTDirector]): Les directeurs d'AST instanciés
            par bibliothèque.
        _flattener (ASTFlattener): L'utilitaire de sérialisation de l'AST
            pour l'inférence.
        _sn_error_pytorch_model (PyTorchModel): Le modèle de détection
            d'erreurs structurelles SyntaxNode.
        _bandit_pytorch_model (PyTorchModel): Le modèle de détection
            de code potentiellement malveillant.
    """
    def __init__(self:Self, config=None) -> None:
        self._name:str = "python"
        self._image_generator: ImageGeneratorStrategy = None
        self._available_lib = []
        self._directors: dict[str, ASTDirector] = {}
        self._flattener = ASTFlattener()
        self._sn_error_pytorch_model: PyTorchModel = None
        self._bandit_pytorch_model: PyTorchModel = None

    @property
    def name(self:Self) -> str:
        """
        Le nom identifiant le langage.

        Returns:
            str: Par défault: 'python'.
        """
        return self._name
    
    @property
    def available_lib(self:Self) -> List[str]:
        """
        La liste des bibliothèques graphiques disponibles pour cette stratégie.

        Returns:
            list: Les noms des bibliothèques supportées.
        """
        return self._available_lib
        
    @property
    def image_generator(self: Self) -> str:
        """
        Le nom du moteur de rendu visuel actif.

        Returns:
            str: Le nom du générateur d'image actuellement assigné.
        """
        return self._image_generator.name

    def get_code_files(self: Self, library: str, data: List[Dict[str, Any]], metadata:Dict[str, Any]) -> BytesIO:
        """
        Génère les fichiers de code source Python à partir du graphe nodal.

        Instancie un `ASTDirector` pour la bibliothèque si nécessaire, génère
        l'AST, le convertit en code source Python et retourne le tout compressé
        dans une archive.

        Args:
            library (str): Le nom de la bibliothèque graphique cible.
            data (List[Dict[str, Any]]): Le graphe nodal configuré par l'utilisateur.
            metadata (Dict[str, Any]): Les métadonnées de la bibliothèque graphique.

        Returns:
            BytesIO: Un flux d'octets contenant l'archive .zip du fichier
                `main_application.py` généré.

        Raises:
            ErrorDetailsContainer: Si les données contiennent des erreurs de validation structurelle.
            ErrorContainer: Si plusieurs groupes d'erreurs de validation sont détectés.
            FatalError: Si une fonction potentiellement malveillante est détectée dans le code utilisateur.
            IllegalImportError: Si un module requis par un composant ne peut pas être importé.
        """
        if library not in self._directors:
            self._directors[library] = ASTDirector(BuilderFactory.get_builder(library))

        ast = self._directors[library].make(data, metadata)
        code = CodeGenerator.generate_code(ast)

        file = CodeGenerator.generate_file("main_application.py", code)
        zip_file = CodeGenerator.generate_zip_files((file,))

        return zip_file
    
    def generate_bitmap(self: Self, library:str, image_generator:ImageGeneratorStrategy, data: Dict[Any, Any], metadata: Dict[Any, Any], target_id:str) -> BytesIO:
        """
        Génère un aperçu visuel pour un composant spécifique du graphe nodal.

        Instancie un `ASTDirector` pour la bibliothèque si nécessaire, génère
        un AST partiel centré sur le composant cible et retourne l'image rendue
        par le générateur offscreen.

        Args:
            library (str): Le nom de la bibliothèque graphique cible.
            image_generator (ImageGeneratorStrategy): Le moteur de rendu visuel à utiliser.
            data (Dict[str, Any]): Le graphe nodal configuré par l'utilisateur.
            metadata (Dict[str, Any]): Les métadonnées de la bibliothèque graphique.
            target_id (str): L'identifiant unique du nœud à rendre.

        Returns:
            BytesIO: Un flux d'octets contenant l'image générée.

        Raises:
            ValueError: Si le générateur d'image n'est pas compatible avec la bibliothèque.
            ErrorDetailsContainer: Si les données contiennent des erreurs de validation structurelle.
            ErrorContainer: Si plusieurs groupes d'erreurs de validation sont détectés.
            FatalError: Si une fonction potentiellement malveillante est détectée dans le code utilisateur.
            IllegalImportError: Si un module requis par un composant ne peut pas être importé.
        """
        if image_generator.name != library:
            raise ValueError("image_generator n'est pas compatible avec la library spécifié.")
        
        if library not in self._directors:
            self._directors[library] = ASTDirector(BuilderFactory.get_builder(library))
            
        self._image_generator = image_generator
        
        tree = self._directors[library].make(data, metadata, target_id)

        return self._image_generator.generate_preview(tree)
    
    def validate_ast(self:Self, library: str, data: Dict[Any, Any], metadata: Dict[Any, Any]) -> bool:
        """
        Valide la cohérence de l'AST généré à partir des données du graphe nodal.

        Instancie un `ASTDirector` pour la bibliothèque si nécessaire et génère
        l'AST complet pour vérifier qu'il ne contient pas d'erreurs structurelles
        ou de références invalides.

        Args:
            library (str): Le nom de la bibliothèque graphique cible.
            data (List[Dict[str, Any]]): Le graphe nodal configuré par l'utilisateur.
            metadata (Dict[str, Any]): Les métadonnées de la bibliothèque graphique.

        Returns:
            bool: True si l'AST généré est valide.

        Raises:
            ErrorDetailsContainer: Si les données contiennent des erreurs de validation structurelle.
            ErrorContainer: Si plusieurs groupes d'erreurs de validation sont détectés.
            FatalError: Si une fonction potentiellement malveillante est détectée dans le code utilisateur.
            IllegalImportError: Si un module requis par un composant ne peut pas être importé.
        """
        if library not in self._directors:
            self._directors[library] = ASTDirector(BuilderFactory.get_builder(library))

        ast = self._directors[library].make(data, metadata)

        return True
    
    def train_ai(self:Self, library:str, metadata: Dict[Any, Any]) -> None:
        """
        Entraîne ou charge les modèles PyTorch d'analyse statique.

        Si les modèles sauvegardés existent déjà sur disque, ils sont chargés
        silencieusement. Sinon, deux modèles sont entraînés : un pour la détection
        d'erreurs structurelles SyntaxNode et un pour la détection de code
        potentiellement malveillant (Bandit), puis sauvegardés sur disque.

        Args:
            library (str): Le nom de la bibliothèque graphique cible.
            metadata: Les métadonnées de la bibliothèque graphique.
        """
        if library not in self._directors:
            self._directors[library] = ASTDirector(BuilderFactory.get_builder(library))

        # Les imports sont fait localement dans la fonction, à cause des conflits avec PySide6.
        import torch
        from torch.utils.data import DataLoader
        
        BaseDataSet.load()

        if not SN_ERROR_MODEL_PATH.exists():
            self._sn_error_pytorch_model = PyTorchModel(len(BaseDataSet._lexical), 32, 64)
            sn_dataset = DatasetFactory.create(TrainingSource.SYNTAX_NODE_ERROR, library, metadata)
            sn_dataloader = DataLoader(sn_dataset, batch_size=32, shuffle=True)
            PythonStrategy._train(self._sn_error_pytorch_model, sn_dataloader, 50)
            torch.save({"state_dict": self._sn_error_pytorch_model.state_dict(), "vocab_size": len(BaseDataSet._lexical)}, SN_ERROR_MODEL_PATH)
        else:
            data = torch.load(SN_ERROR_MODEL_PATH)
            self._sn_error_pytorch_model = PyTorchModel(data["vocab_size"], 32, 64)
            self._sn_error_pytorch_model.load_state_dict(data["state_dict"])

        if not BANDIT_MODEL_PATH.exists():
            self._bandit_pytorch_model = PyTorchModel(len(BaseDataSet._lexical), 32, 64)
            bandit_dataset = DatasetFactory.create(TrainingSource.BANDIT)
            bandit_dataloader = DataLoader(bandit_dataset, batch_size=32, shuffle=True)
            self._train(self._bandit_pytorch_model, bandit_dataloader, 50)
            torch.save({"state_dict": self._bandit_pytorch_model.state_dict(), "vocab_size": len(BaseDataSet._lexical)}, BANDIT_MODEL_PATH)
        else:
            data = torch.load(BANDIT_MODEL_PATH)
            self._bandit_pytorch_model = PyTorchModel(data["vocab_size"], 32, 64)
            self._bandit_pytorch_model.load_state_dict(data["state_dict"])

    @staticmethod
    def _train(model: PyTorchModel, dataloader, epochs: int):
        """
        Boucle d'entraînement d'un modèle PyTorch.

        Méthode interne destinée à être appelée par `train_ai`. Utilise une
        fonction de perte BCE (Binary Cross Entropy) et l'optimiseur Adam.

        Args:
            model (PyTorchModel): Le modèle à entraîner.
            dataloader (DataLoader): Le chargeur de données fournissant les
                batches d'entraînement.
            epochs (int): Le nombre d'époques d'entraînement.
        """
        # Les imports sont fait localement dans la fonction, à cause des conflits avec PySide6.
        from torch.optim.adam import Adam
        from torch import squeeze
        import torch.nn as nn

        loss = nn.BCELoss()
        optimizer = Adam(model.parameters(), 0.001)

        for epoch in range(epochs):
            loss_accum = 0
            nb_batch = 0
            for batch, labels in dataloader:
                optimizer.zero_grad()
                predictions = model(batch)
                output = loss(squeeze(predictions, 1), labels)
                output.backward()
                optimizer.step()
                loss_accum += output.item()
                nb_batch += 1
            print(f"Moyenne de loss : {loss_accum / nb_batch}")

    def predict(self, library:str, data: Dict[Any, Any], metadata: Dict[str, Any]) -> float:
        """
        Effectue une prédiction sur le code utilisateur via les modèles PyTorch.

        Si les modèles ne sont pas encore chargés, l'entraînement est déclenché
        silencieusement via `train_ai`. Retourne le score le plus élevé entre
        le modèle de détection d'erreurs structurelles SyntaxNode et le modèle
        de détection de code potentiellement malveillant (Bandit).

        Args:
            library (str): Le nom de la bibliothèque graphique cible.
            data (List[Dict[str, Any]]): Le graphe nodal configuré par l'utilisateur.
            metadata (Dict[str, Any]): Les métadonnées de la bibliothèque graphique.

        Returns:
            float: Le score de risque le plus élevé entre les deux modèles,
                à comparer avec les seuils de `PredictionValue`.
        """
        if library not in self._directors:
            self._directors[library] = ASTDirector(BuilderFactory.get_builder(library))

        if self._sn_error_pytorch_model is None or self._bandit_pytorch_model is None:
            self.train_ai(library, metadata)

        from torch import no_grad, unsqueeze
        with no_grad():
            tree = self._directors[library].make(data, metadata)
            flatten_ast = self._flattener.flatten(tree)

            x = unsqueeze(BaseDataSet._data_into_tensor(flatten_ast, False)[0], 0)
            
            result = max(self._sn_error_pytorch_model(x).item(), self._bandit_pytorch_model(x).item())
        
        return result