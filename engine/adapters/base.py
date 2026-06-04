"""
Interface abstraite pour les adaptateurs de métadonnées.

Ce module définit le contrat (Abstract Base Class) que tous les adaptateurs
de métadonnées spécifiques à une bibliothèque graphique doivent respecter
pour être utilisables par les stratégies du moteur SyntaxNode.

Classes
-------
MetadataAdapter: Contrat abstrait pour l'extraction des métadonnées d'un composant.
"""

from abc import ABC, abstractmethod
from typing import Any, Self, Dict


class MetadataAdapter(ABC):
    """
    Contrat abstrait pour l'extraction des métadonnées d'un composant.

    Définit l'interface commune que tout adaptateur spécifique à une
    bibliothèque graphique (ex: Qt, Tkinter) doit implémenter pour extraire
    et exposer les métadonnées d'une classe de composant.
    """

    def __init__(self: Self, cls: type) -> None:
        """
        Initialise l'adaptateur avec la classe à introspecter.

        Args:
            cls (type): La classe du composant dont les métadonnées seront extraites.
        """
        self._cls = cls

    @property
    def cls(self: Self) -> type:
        """
        La classe du composant en cours d'introspection.

        Returns:
            type: La classe passée lors de l'initialisation.
        """
        return self._cls

    @property
    @abstractmethod
    def meta(self: Self) -> Any:
        """
        L'objet de métadonnées brut fourni par le framework de la bibliothèque.

        Returns:
            Any: L'objet de métadonnées natif (ex: QMetaObject pour Qt).
        """
        pass

    @property
    @abstractmethod
    def class_name(self: Self) -> str:
        """
        Le nom de la classe du composant.

        Returns:
            str: Le nom de la classe (ex: 'QPushButton').
        """
        pass

    @property
    @abstractmethod
    def category(self: Self) -> str:
        """
        La catégorie du composant dans la hiérarchie de la bibliothèque.

        Returns:
            str: La catégorie (ex: 'widget', 'layout', 'core').
        """
        pass

    @property
    @abstractmethod
    def parent_class(self: Self) -> str:
        """
        Le nom de la classe parente directe du composant.

        Returns:
            str: Le nom de la classe parente (ex: 'QAbstractButton').
        """
        pass

    @property
    @abstractmethod
    def module(self: Self) -> str:
        """
        Le nom du module Python contenant la classe du composant.

        Returns:
            str: Le chemin du module (ex: 'PySide6.QtWidgets').
        """
        pass

    @property
    @abstractmethod
    def is_abstract(self: Self) -> bool:
        """
        Indique si la classe du composant est abstraite (non instanciable).

        Returns:
            bool: True si la classe ne peut pas être instanciée directement,
                False sinon.
        """
        pass

    @property
    @abstractmethod
    def properties(self: Self) -> Dict[str, Any]:
        """
        Les propriétés du composant disponibles pour la configuration.

        Returns:
            Dict[str, Any]: Un dictionnaire des propriétés inscriptibles
                du composant, indexé par nom.
        """
        pass

    @property
    @abstractmethod
    def methods(self: Self) -> Dict[str, Any]:
        """
        Les méthodes (signaux et slots) du composant.

        Returns:
            Dict[str, Any]: Un dictionnaire des signaux et slots du composant,
                organisé par type ('signal', 'slot').
        """
        pass

    @abstractmethod
    def to_dict(self: Self) -> Dict[str, Any]:
        """
        Sérialise les métadonnées du composant en un dictionnaire.

        Returns:
            Dict[str, Any]: Un dictionnaire structuré contenant toutes les
                métadonnées du composant (catégorie, nom, module, propriétés,
                méthodes, etc.).
        """
        pass

    @abstractmethod
    def _safe_instantiate(self: Self) -> Any:
        """
        Tente d'instancier la classe du composant sans arguments.

        Méthode interne utilisée pour déterminer si la classe est abstraite
        et pour extraire les valeurs par défaut de ses propriétés.

        Returns:
            Any: L'instance créée, ou None si l'instanciation échoue.
        """
        pass
