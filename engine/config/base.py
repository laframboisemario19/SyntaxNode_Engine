"""
Interface abstraite pour les configurations de bibliothèques graphiques.

Ce module définit le contrat (Abstract Base Class) que toutes les configurations
spécifiques à une bibliothèque graphique doivent respecter pour être utilisables
par les adaptateurs et les stratégies du moteur SyntaxNode.

Classes
-------
BaseConfig: Contrat abstrait pour les configurations de bibliothèques graphiques.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple


class BaseConfig(ABC):
    """
    Contrat abstrait pour les configurations de bibliothèques graphiques.

    Définit l'interface commune que toute configuration concrète (ex:
    `TestConfig`, `DefaultConfig`) doit implémenter pour exposer les
    types, composants et paramètres supportés à l'adaptateur de métadonnées.
    """

    @property
    @abstractmethod
    def objects_implemented(self) -> Tuple[type, ...]:
        """
        Les classes de composants graphiques supportées par cette configuration.

        Returns:
            Tuple[type, ...]: Un tuple des classes instanciables et introspecables
                (ex: QWidget, QPushButton, QVBoxLayout).
        """
        pass

    @property
    @abstractmethod
    def primitives_types(self) -> Tuple[type, ...]:
        """
        Les types primitifs Python supportés pour les valeurs de propriétés.

        Returns:
            Tuple[type, ...]: Un tuple des types primitifs supportés
                (ex: int, str, bool, float).
        """
        pass

    @property
    @abstractmethod
    def complex_types_implemented(self) -> Dict[type, Any]:
        """
        Les types complexes Qt supportés et leur description de sérialisation.

        Returns:
            Dict[type, Any]: Un dictionnaire associant chaque type complexe
                (ex: QSizePolicy, QFont) à un tuple contenant son nom générique
                et le dictionnaire de ses attributs.
        """
        pass

    @property
    @abstractmethod
    def enum_implemented(self) -> Tuple[type, ...]:
        """
        Les types d'énumération Qt supportés pour les propriétés.

        Returns:
            Tuple[type, ...]: Un tuple des types d'énumération supportés
                (ex: Qt.FocusPolicy, QFrame.Shape).
        """
        pass

    @property
    @abstractmethod
    def flags_implemented(self) -> Tuple[type, ...]:
        """
        Les types de flags Qt supportés pour les propriétés.

        Returns:
            Tuple[type, ...]: Un tuple des types de flags supportés
                (ex: Qt.AlignmentFlag, Qt.InputMethodHint).
        """
        pass

    @property
    @abstractmethod
    def params_implemented(self) -> Tuple[str, ...]:
        """
        Les noms de paramètres de propriétés supportés par cette configuration.

        Returns:
            Tuple[str, ...]: Un tuple des noms de propriétés en snake_case
                dont l'introspection est activée (ex: 'text', 'alignment').
        """
        pass

    @property
    @abstractmethod
    def type_map(self) -> Dict[str, type]:
        """
        La table de correspondance entre les noms de types C++/Qt et les types Python.

        Returns:
            Dict[str, type]: Un dictionnaire associant les noms de types tels
                qu'exposés par QMetaProperty (ex: 'QString', 'Qt::FocusPolicy')
                aux types Python correspondants.
        """
        pass

    @abstractmethod
    def is_param_supported(self, raw_name: str) -> bool:
        """
        Vérifie si un nom de paramètre est supporté par cette configuration.

        Args:
            raw_name (str): Le nom du paramètre en snake_case à vérifier.

        Returns:
            bool: True si le paramètre est dans la liste des paramètres supportés,
                False sinon.
        """
        pass
