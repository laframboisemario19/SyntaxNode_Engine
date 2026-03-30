"""
Module définissant le moteur principal de SyntaxNode.

Ce module contient la classe `SyntaxNodeEngine`, qui agit comme le point central
pour gérer l'état et coordonner les stratégies liées aux langages de programmation 
et aux bibliothèques d'interface graphique.
"""

from typing import Any

from .strategies import StrategyFactory, StrategyType, ConfigType

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
        >>> engine.set_lib("qt")
        >>> print(engine.current_lang)
        'python'
    """
    def __init__(self) -> None:
        """Initialise le moteur avec aucune stratégie sélectionnée par défaut."""
        self._current_lang_strategy = None
        self._current_lib_strategy = None

    @property
    def available_lang(self) -> list[str]:
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
    def available_lib(self) -> list[str]:
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
    def current_lang(self) -> str:
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
    def current_lib(self) -> str:
        """
        Obtient le nom de la bibliothèque actuellement sélectionnée.

        Returns:
            str: Le nom de la bibliothèque courante, ou une chaîne vide si aucune n'est sélectionnée.
        """
        if self._current_lib_strategy:  
            return self._current_lib_strategy.name
        else:
            return ""
    
    def set_language(self, language:str) -> None:
        """
        Définit la stratégie du langage de programmation à utiliser.

        Args:
            language (str): Le nom du langage à instancier.

        Examples:
            >>> engine = SyntaxNodeEngine()
            >>> engine.set_language("python")
        """
        self._current_lang_strategy = StrategyFactory.get_strategy(StrategyType.LANGUAGE, language)

    def set_lib(self, library:str, config:ConfigType = ConfigType.TEST) -> None:
        """
        Définit la stratégie de la bibliothèque à utiliser.

        Un langage doit obligatoirement être défini avant d'assigner une bibliothèque.

        Args:
            library (str): Le nom de la bibliothèque à instancier.
            config (ConfigType, optional): La configuration associée. Par défaut `ConfigType.TEST`.

        Raises:
            RuntimeError: Si la méthode est appelée avant qu'un langage ne soit défini.

        Examples:
            >>> engine = SyntaxNodeEngine()
            >>> engine.set_language("python")
            >>> engine.set_lib("qt", ConfigType.DEFAULT)
        """
        if not self._current_lang_strategy:
            raise RuntimeError("Erreur: Vous devez sélectionner un langage avant de définir la librairie.")
        self._current_lib_strategy = StrategyFactory.get_strategy(StrategyType.LIBRARY, library, config)

    def get_meta_objects(self) -> dict[str, Any]:
        """
        Récupère les objets et métadonnées associés à la bibliothèque courante.

        Returns:
            dict[str, Any]: Un dictionnaire contenant les objets structurels de la bibliothèque.

        Raises:
            RuntimeError: Si aucune bibliothèque n'a été préalablement définie.

        Examples:
            >>> engine.set_language("python")
            >>> engine.set_lib("qt")
            >>> meta = engine.get_meta_objects()
            >>> print(meta["core"][0]["name"]
            dict_keys('QObject')
        """
        if not self._current_lib_strategy:
            raise RuntimeError("Erreur : Aucune librairie n'a été sélectionnée")
        return self._current_lib_strategy.get_meta_objects()
    
    def get_code_files(self, data):
        if not self._current_lib_strategy:
            raise RuntimeError("Erreur : Aucune librairie n'a été sélectionnée")
        metadata = self._current_lib_strategy.metadata
        return self._current_lang_strategy.get_code_files(self.current_lib, data, metadata)