"""
Paquet des stratégies de génération pour le moteur SyntaxNode.

Ce paquet implémente le patron de conception Stratégie pour découpler
la logique de génération de code et de rendu visuel des implémentations
spécifiques aux langages et aux bibliothèques graphiques.

Classes
-------
LanguageStrategy: Contrat abstrait pour les stratégies de génération de code.
LibraryStrategy: Contrat abstrait pour les stratégies de gestion des métadonnées.
ImageGeneratorStrategy: Contrat abstrait pour les moteurs de rendu visuel offscreen.
PythonStrategy: Stratégie concrète de génération de code pour le langage Python.
QtStrategy: Stratégie concrète de gestion des métadonnées pour la bibliothèque Qt.
QtOffScreenGenerator: Moteur de rendu visuel offscreen pour les aperçus Qt.
StrategyFactory: Usine centralisant l'instanciation des stratégies.
StrategyType: Énumération des types de stratégies disponibles.
ConfigType: Énumération des niveaux de configuration pour les bibliothèques.
"""

from .python_strategy import PythonStrategy
from .qt_strategy import QtStrategy, QtOffScreenGenerator
from .factory import StrategyType, StrategyFactory, ConfigType
from .base import LanguageStrategy, LibraryStrategy, ImageGeneratorStrategy

__all__ = ["PythonStrategy", "QtStrategy", "QtOffScreenGenerator", "StrategyType", "StrategyFactory", "ConfigType", "LanguageStrategy", "LibraryStrategy", "ImageGeneratorStrategy"]