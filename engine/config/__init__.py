"""
Paquet de configuration des bibliothèques graphiques pour le moteur SyntaxNode.

Ce paquet expose les classes de configuration qui définissent les types,
composants et paramètres supportés pour l'introspection et la génération
de code avec chaque bibliothèque graphique.

Classes
-------
BaseConfig: Contrat abstrait pour les configurations de bibliothèques graphiques.
DefaultConfig: Configuration standard pour un usage en production avec Qt/PySide6.
TestConfig: Configuration minimale pour les tests et le développement.
ExtendedConfig: Configuration étendue avec des fonctionnalités supplémentaires.
"""

from .base import BaseConfig
from .default import DefaultConfig
from .extended import ExtendedConfig
from .test import TestConfig

__all__ = ["BaseConfig", "DefaultConfig", "ExtendedConfig", "TestConfig"]
