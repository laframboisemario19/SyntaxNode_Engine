"""
Paquet d'analyse statique du code utilisateur pour le moteur SyntaxNode.

Ce paquet fournit les outils d'entraînement et d'inférence des modèles PyTorch
utilisés pour la détection d'erreurs structurelles et de code potentiellement
malveillant dans les projets SyntaxNode.

Classes
-------
PyTorchModel: Réseau de neurones GRU pour la classification d'AST aplatis.
TrainingSource: Énumération des sources de données d'entraînement.
BaseDataSet: Classe de base abstraite pour les jeux de données PyTorch.
BugsInPyDataset: Jeu de données basé sur des fichiers Python avec bugs.
BanditDataset: Jeu de données basé sur des fichiers Python analysés par Bandit.
SyntaxNodeDataset: Jeu de données basé sur des projets SyntaxNode JSON.
DatasetFactory: Usine instanciant le bon jeu de données selon la source.
"""

from .pytorch_model import PyTorchModel
from .dataset import DatasetFactory, TrainingSource, BaseDataSet, SyntaxNodeDataset, BanditDataset, BugsInPyDataset

__all__ = ["PyTorchModel", "DatasetFactory", "TrainingSource", "BaseDataSet", "SyntaxNodeDataset", "BanditDataset", "BugsInPyDataset"]
