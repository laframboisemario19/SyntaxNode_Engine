"""
Module définissant le moteur principal de SyntaxNode.

Ce module contient la classe `SyntaxNodeEngine`, qui agit comme le point central
pour gérer l'état et coordonner les stratégies liées aux langages de programmation 
et aux bibliothèques d'interface graphique.
"""

from typing import Any, Self, Dict, List, Tuple
from io import BytesIO

from .strategies import StrategyFactory, StrategyType, ConfigType
from .error import StrategyNotFoundError
from .validators import JsonValidator

class SyntaxNodeEngine():
    """
    Moteur principal gérant l'état et les stratégies de génération pour SyntaxNode.

    Cette classe utilise le patron de conception Stratégie pour découpler
    la logique de l'application des implémentations spécifiques aux langages
    et aux bibliothèques.

    Attributes:
        _current_lang_strategy: L'instance de la stratégie du langage actuellement sélectionné.
        _current_lib_strategy: L'instance de la stratégie de la bibliothèque actuellement sélectionnée.
    Examples:
        >>> engine = SyntaxNodeEngine()
        >>> engine.set_language("python")
        >>> engine.set_lib("qt", ConfigType.TEST)
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
        json_valid = JsonValidator.validate_data(data)
        metadata = self._current_lib_strategy.metadata
        ast_valid = self._current_lang_strategy.validate_ast(self.current_lib, data, metadata)

        return json_valid and ast_valid


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
        if not self._current_lib_strategy:
            raise StrategyNotFoundError("Aucune librairie n'a été sélectionnée")
        
        metadata = self._current_lib_strategy.metadata
        self._current_lang_strategy.train_ai(self.current_lib, metadata)

    def predict(self:Self, data) -> float:
        if not self._current_lib_strategy:
            raise StrategyNotFoundError("Aucune librairie n'a été sélectionnée")
        
        metadata = self._current_lib_strategy.metadata
        return self._current_lang_strategy.predict(self.current_lib, data, metadata)
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()
    print("test complété")