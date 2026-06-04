"""
Configuration étendue pour les bibliothèques graphiques Qt.

Ce module fournit la classe `ExtendedConfig`, une configuration étendue
incluant des composants et des types supplémentaires par rapport à
`DefaultConfig`. Son implémentation est réservée pour usage futur.

Classes
-------
ExtendedConfig: Configuration étendue avec des fonctionnalités supplémentaires.
"""

from typing import Any, Dict, Tuple

from .base import BaseConfig


class ExtendedConfig(BaseConfig):
    """
    Configuration étendue avec des fonctionnalités supplémentaires.

    Placeholder destiné à une future implémentation d'une configuration
    Qt étendue. Toutes les propriétés retournent actuellement None.
    """

    @property
    def objects_implemented(self) -> Tuple[type, ...]:
        """
        Les classes de composants graphiques supportées par cette configuration.

        Returns:
            Tuple[type, ...]: Les classes de composants supportées.
        """
        pass

    @property
    def primitives_types(self) -> Tuple[type, ...]:
        """
        Les types primitifs Python supportés pour les valeurs de propriétés.

        Returns:
            Tuple[type, ...]: Les types primitifs supportés.
        """
        pass

    @property
    def complex_types_implemented(self) -> Dict[type, Any]:
        """
        Les types complexes Qt supportés et leur description de sérialisation.

        Returns:
            Dict[type, Any]: Les types complexes supportés.
        """
        pass

    @property
    def enum_implemented(self) -> Tuple[type, ...]:
        """
        Les types d'énumération Qt supportés pour les propriétés.

        Returns:
            Tuple[type, ...]: Les types d'énumération supportés.
        """
        pass

    @property
    def flags_implemented(self) -> Tuple[type, ...]:
        """
        Les types de flags Qt supportés pour les propriétés.

        Returns:
            Tuple[type, ...]: Les types de flags supportés.
        """
        pass

    @property
    def params_implemented(self) -> Tuple[str, ...]:
        """
        Les noms de paramètres de propriétés supportés par cette configuration.

        Returns:
            Tuple[str, ...]: Les noms de propriétés supportées.
        """
        pass

    @property
    def type_map(self) -> Dict[str, type]:
        """
        La table de correspondance entre les noms de types C++/Qt et les types Python.

        Returns:
            Dict[str, type]: La table de correspondance des types.
        """
        pass

    def is_param_supported(self, raw_name: str) -> bool:
        """
        Vérifie si un nom de paramètre est supporté par cette configuration.

        Args:
            raw_name (str): Le nom du paramètre en snake_case à vérifier.

        Returns:
            bool: True si le paramètre est supporté, False sinon.
        """
        pass
