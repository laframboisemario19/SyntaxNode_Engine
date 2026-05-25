"""
Module définissant le moteur principal de SyntaxNode.

Ce module contient la classe `SyntaxNodeEngine`, qui agit comme le point central
pour gérer l'état et coordonner les stratégies liées aux langages de programmation 
et aux bibliothèques d'interface graphique. Il sert également de pont vers le modèle
PyTorch pour l'analyse statique du code utilisateur.

Classes
-------
    SyntaxNodeEngine: Moteur principal orchestrant les stratégies de génération.
    PredictionValue: Énumération des seuils de décision pour l'analyse statique.
"""

from typing import Any, Self, Dict, List, Tuple
from io import BytesIO
from enum import Enum, auto

from .strategies import StrategyFactory, StrategyType, ConfigType
from .error import StrategyNotFoundError
from .validators import JsonValidator

class PredictionValue(Enum):
    """
    Énumération des seuils de décision pour l'analyse statique du code utilisateur.

    Ces valeurs sont utilisées par le moteur pour déterminer si le code généré
    est considéré sûr ou non selon le modèle PyTorch.

    Attributes:
        SAFE (float): Seuil indiquant que le code est considéré sûr (0).
        UNSAFE (float): Seuil indiquant que le code est considéré non sûr (0.4).
    """
    SAFE = 0
    UNSAFE = 0.4

class SyntaxNodeEngine():
    """
    Moteur principal gérant l'état et les stratégies de génération pour SyntaxNode.

    Cette classe utilise le patron de conception Stratégie pour découpler
    la logique de l'application des implémentations spécifiques aux langages
    et aux bibliothèques. Elle sert également de pont vers le modèle PyTorch
    pour l'entraînement et l'analyse statique du code utilisateur.

    Attributes:
        _current_lang_strategy: L'instance de la stratégie du langage actuellement sélectionné.
        _current_lib_strategy: L'instance de la stratégie de la bibliothèque actuellement sélectionnée.
    Examples:
        >>> engine = SyntaxNodeEngine()
        >>> engine.set_language("python")
        >>> engine.set_lib("qt", ConfigType.DEFAULT)
        >>> print(engine.current_lang)
        python
    """
    def __init__(self:Self) -> None:
        """Initialise le moteur avec aucune stratégie sélectionnée par défaut."""
        self._current_lang_strategy = None
        self._current_lib_strategy = None
        
    @property
    def available_lang(self:Self) -> list[str]:
        """
        Récupère la liste des langages de programmation disponibles.

        Returns:
            list[str]: Une liste des noms des langages supportés par l'usine de stratégies.

        Examples:
            >>> engine = SyntaxNodeEngine()
            >>> engine.available_lang
            ['python']
        """
        return StrategyFactory.get_available(StrategyType.LANGUAGE)
    
    @property
    def available_lib(self:Self) -> list[str]:
        """
        Récupère la liste des bibliothèques disponibles.

        Returns:
            list[str]: Une liste des noms des bibliothèques supportées par l'usine de stratégies.

        Examples:
            >>> engine = SyntaxNodeEngine()
            >>> engine.available_lib
            ['qt']
        """
        return StrategyFactory.get_available(StrategyType.LIBRARY)
    
    @property
    def current_lang(self:Self) -> str:
        """
        Obtient le nom du langage actuellement sélectionné.

        Returns:
            str: Le nom du langage courant, ou une chaîne vide si aucun n'est sélectionné.
        """
        if self._current_lang_strategy:
            return self._current_lang_strategy.name
        else:
            return ""
    
    @property
    def current_lib(self:Self) -> str:
        """
        Obtient le nom de la bibliothèque actuellement sélectionnée.

        Returns:
            str: Le nom de la bibliothèque courante, ou une chaîne vide si aucune n'est sélectionnée.
        """
        if self._current_lib_strategy:  
            return self._current_lib_strategy.name
        else:
            return ""
    
    def set_language(self:Self, language:str) -> None:
        """
        Définit la stratégie du langage de programmation à utiliser.

        Args:
            language (str): Le nom du langage à instancier.

        Examples:
            >>> engine = SyntaxNodeEngine()
            >>> engine.set_language("python")
        """
        self._current_lang_strategy = StrategyFactory.get_strategy(StrategyType.LANGUAGE, language)

    def set_lib(self:Self, library:str, config:ConfigType = ConfigType.TEST) -> None:
        """
        Définit la stratégie de la bibliothèque à utiliser.

        Un langage doit obligatoirement être défini avant d'assigner une bibliothèque.

        Args:
            library (str): Le nom de la bibliothèque à instancier.
            config (ConfigType, optional): La configuration associée. Par défaut `ConfigType.TEST`.

        Raises:
            StrategyNotFoundError: Si la méthode est appelée avant qu'un langage ne soit défini.

        Examples:
            >>> engine = SyntaxNodeEngine()
            >>> engine.set_language("python")
            >>> engine.set_lib("qt", ConfigType.DEFAULT)
        """
        if not self._current_lang_strategy:
            raise StrategyNotFoundError("Vous devez sélectionner un langage avant de définir la librairie.")
        self._current_lib_strategy = StrategyFactory.get_strategy(StrategyType.LIBRARY, library, config)

    def get_meta_objects(self:Self) -> Dict[str, Any]:
        """
        Récupère les objets et métadonnées associés à la bibliothèque courante.

        Returns:
            Dict[str, Any]: Un dictionnaire contenant les objets structurels de la bibliothèque.

        Raises:
            StrategyNotFoundError: Si aucune bibliothèque n'a été préalablement définie.

        Examples:
            >>> engine = SyntaxNodeEngine()
            >>> engine.set_language("python")
            >>> engine.set_lib("qt")
            >>> meta = engine.get_meta_objects()
            >>> print(meta["core"][0]["name"])
            QObject
        """
        if not self._current_lib_strategy:
            raise StrategyNotFoundError("Aucune librairie n'a été sélectionnée")
        return self._current_lib_strategy.get_meta_objects()
    
    def validate_data(self:Self, data:List[Dict[str, Any]]) -> bool:
        """
        Valide les données du graphe nodal sur trois niveaux.

        Vérifie la conformité JSON des données, la validité de l'AST généré,
        et effectue une analyse statique via le modèle PyTorch pour détecter
        du code potentiellement non sûr.

        Args:
            data (List[Dict[str, Any]]): Une liste de dictionnaires représentant
                les nœuds et les connexions du graphe configuré par l'utilisateur.

        Returns:
            bool: True si les données sont valides et le code considéré sûr,
                False sinon.

        Raises:
            StrategyNotFoundError: Si aucune bibliothèque n'a été préalablement définie.
            TypeJsonFormatError: Si le type des données passées est invalide.
            RootError: Si le projet ne respecte pas la structure de composants requise.
            IllegalImportError: Si un module requis par un composant ne peut pas être importé.
            FatalError: Si une fonction potentiellement malveillante est détectée dans le code utilisateur.
            ErrorDetailsContainer: Si les données contiennent des erreurs de validation structurelle.
            ErrorContainer: Si plusieurs groupes d'erreurs de validation sont détectés.

        Examples:
        >>> try:
        ...     is_valid = engine.validate_data(data)
        ... except ErrorContainer as e:
        ...     for error_details_container in e.error_list:
        ...         for detail in error_details_container.error_detail_list:
        ...             print(f"Erreur : {detail.msg}")
        ...             print(f"Emplacement : {' -> '.join(detail.loc)}")
        ...             if detail.focus_id:
        ...                 print(f"Id du composant à surligner : {detail.focus_id}")
        """
        json_valid = JsonValidator.validate_data(data)
        metadata = self._current_lib_strategy.metadata
        ast_valid = self._current_lang_strategy.validate_ast(self.current_lib, data, metadata)
        ai_analyze = self._predict(data)

        return json_valid and ast_valid and ai_analyze


    def get_code_files(self: Self, data:List[Dict[str, Any]]) -> BytesIO:
        """
        Génère les fichiers de code source à partir des données de l'interface visuelle.

        Cette méthode orchestre la génération en récupérant les métadonnées de la 
        bibliothèque courante et en déléguant la création de l'AST et du code source 
        final à la stratégie du langage sélectionné. Les fichiers générés sont 
        compressés et retournés sous forme de flux d'octets.

        Args:
            data (List[Dict[str, Any]]): Une liste de dictionnaires représentant 
                les nœuds et les connexions du graphe configuré par l'utilisateur.

        Returns:
            BytesIO: Un flux de données en mémoire contenant l'archive (ex: .zip) 
            des fichiers de code source générés.

        Raises:
            StrategyNotFoundError: Si aucune bibliothèque n'a été préalablement définie.
            TypeJsonFormatError: Si le type des données passées est invalide.
            RootError: Si le projet ne respecte pas la structure de composants requise.
            IllegalImportError: Si un module requis par un composant ne peut pas être importé.
            FatalError: Si une fonction potentiellement malveillante est détectée dans le code utilisateur.
            ErrorDetailsContainer: Si les données contiennent des erreurs de validation structurelle.
            ErrorContainer: Si plusieurs groupes d'erreurs de validation sont détectés.

        Examples:
            >>> engine = SyntaxNodeEngine()
            >>> engine.set_language("python")
            >>> engine.set_lib("qt")
            >>> # Requiert une liste de dictionnaires respectant le schéma SyntaxNode
            >>> donnees_valides = [{"id": "root", "type": "MyApp", "children": [...]}] # doctest: +SKIP
            >>> archive_buffer = engine.get_code_files(donnees_valides) # doctest: +SKIP
            >>> type(archive_buffer).__name__ # doctest: +SKIP
            'BytesIO'
        """
        if not self._current_lib_strategy:
            raise StrategyNotFoundError("Aucune librairie n'a été sélectionnée")
        
        JsonValidator.validate_data(data)
        metadata = self._current_lib_strategy.metadata
        return self._current_lang_strategy.get_code_files(self.current_lib, data, metadata)
    
    def generate_bitmap(self: Self, data:List[Dict[str, Any]], target_id:str) -> BytesIO:
        """
        Génère un aperçu visuel (bitmap/buffer) pour un composant spécifique du graphe.

        Cette méthode instancie dynamiquement la stratégie de génération d'image 
        correspondante à la bibliothèque (ex: rendu offscreen en mémoire pour Qt) 
        et délègue l'exécution et l'extraction de l'image à la stratégie du langage.

        Args:
            data (List[Dict[str, Any]]): Une liste de dictionnaires représentant 
                les nœuds et les connexions du graphe configuré par l'utilisateur.
            target_id (str): L'identifiant unique du nœud (composant) pour lequel 
                générer l'aperçu visuel.

        Returns:
            BytesIO: Le flux de données de l'image générée, prêt à être expédié au frontend.

        Raises:
            StrategyNotFoundError: Si aucune bibliothèque n'a été préalablement définie.
            TypeJsonFormatError: Si le type des données passées est invalide.
            RootError: Si le projet ne respecte pas la structure de composants requise.
            IllegalImportError: Si un module requis par un composant ne peut pas être importé.
            FatalError: Si une fonction potentiellement malveillante est détectée dans le code utilisateur.
            ErrorDetailsContainer: Si les données contiennent des erreurs de validation structurelle.
            ErrorContainer: Si plusieurs groupes d'erreurs de validation sont détectés.

        Examples:
            >>> engine = SyntaxNodeEngine()
            >>> engine.set_language("python")
            >>> engine.set_lib("qt")
            >>> # Requiert une liste de dictionnaires respectant le schéma SyntaxNode
            >>> donnees_valides = [{"id": "root", "type": "MyApp", "children": [...]}] # doctest: +SKIP
            >>> image_buffer = engine.generate_bitmap(donnees_valides, "root") # doctest: +SKIP
            >>> type(image_buffer).__name__ # doctest: +SKIP
            'BytesIO'
        """
        if not self._current_lib_strategy:
            raise StrategyNotFoundError("Aucune librairie n'a été sélectionnée")
        
        JsonValidator.validate_data(data)
        metadata = self._current_lib_strategy.metadata
        strategy = StrategyFactory.get_strategy(StrategyType.IMG_GENERATOR, self.current_lib)

        return self._current_lang_strategy.generate_bitmap(self.current_lib, strategy, data, metadata, target_id)

    def train_ai(self:Self) -> None:
        """
        Déclenche l'entraînement du modèle PyTorch pour l'analyse statique.

        L'acquisition des données d'entraînement est gérée à l'interne par une
        factory dédiée. Un langage et une bibliothèque doivent obligatoirement
        être définis avant d'appeler cette méthode.

        Raises:
            StrategyNotFoundError: Si aucune bibliothèque n'a été préalablement définie.
        """
        if not self._current_lib_strategy:
            raise StrategyNotFoundError("Aucune librairie n'a été sélectionnée")
        
        metadata = self._current_lib_strategy.metadata
        self._current_lang_strategy.train_ai(self.current_lib, metadata)

    def _predict(self:Self, data: List[Dict[str, Any]]) -> float:
        """
        Analyse statique du code utilisateur via le modèle PyTorch.

        Cette méthode est destinée à être appelée par `validate_data` et non
        directement par l'utilisateur. Si le modèle n'est pas encore entraîné,
        l'entraînement est effectué silencieusement à l'interne avant la prédiction.

        Args:
            data (List[Dict[str, Any]]): Une liste de dictionnaires représentant
                les nœuds et les connexions du graphe configuré par l'utilisateur.

        Returns:
            bool: True si le code est considéré sûr selon le seuil de `PredictionValue.SAFE`,
                False sinon.

        Raises:
            StrategyNotFoundError: Si aucune bibliothèque n'a été préalablement définie.
        """
        if not self._current_lib_strategy:
            raise StrategyNotFoundError("Aucune librairie n'a été sélectionnée")
        
        metadata = self._current_lib_strategy.metadata

        result = self._current_lang_strategy.predict(self.current_lib, data, metadata)
        
        return result >= PredictionValue.SAFE.value
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()
    print("test complété")