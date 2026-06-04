"""
Usine de constructeurs d'AST pour le moteur SyntaxNode.

Ce module implémente le patron de conception Fabrique (Factory) pour
centraliser l'instanciation des constructeurs d'AST spécifiques à chaque
bibliothèque graphique supportée.

Classes
-------
BuilderFactory: Classe utilitaire statique agissant comme usine de constructeurs d'AST.
"""

from typing import Dict, Type

from .qt_ast_builder import QtASTBuilder
from .ast_builder import ASTBuilder


class BuilderFactory:
    """
    Classe utilitaire statique agissant comme usine de constructeurs d'AST.

    Centralise l'instanciation des constructeurs d'AST en associant chaque
    nom de bibliothèque à sa classe de constructeur. L'ajout d'une nouvelle
    bibliothèque ne nécessite que l'enregistrement de sa classe dans `_builders`.

    Attributes:
        _builders (Dict[str, Type[ASTBuilder]]): Registre des classes de
            constructeurs disponibles, indexé par nom de bibliothèque.
    """

    _builders: Dict[str, Type[ASTBuilder]] = {"qt": QtASTBuilder}

    @classmethod
    def get_builder(cls, library: str) -> ASTBuilder:
        """
        Instancie et retourne le constructeur d'AST correspondant à la bibliothèque.

        Args:
            library (str): Le nom de la bibliothèque graphique cible (ex: 'qt').

        Returns:
            ASTBuilder: Une nouvelle instance du constructeur d'AST associé.

        Raises:
            KeyError: Si le nom de la bibliothèque n'est pas enregistré dans
                `_builders`.
        """
        return cls._builders[library]()
