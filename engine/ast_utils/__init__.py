"""
Paquet de construction et d'analyse d'arbres syntaxiques (AST).

Ce paquet regroupe les outils de génération, de validation et de sérialisation
des arbres syntaxiques Python produits à partir du graphe nodal SyntaxNode.

Classes
-------
ASTBuilder: Contrat abstrait pour la construction d'un AST Python.
QtASTBuilder: Constructeur d'AST concret pour la bibliothèque Qt/PySide6.
ASTDirector: Orchestrateur de la construction d'un AST à partir du graphe nodal.
BuilderFactory: Usine d'instanciation des constructeurs d'AST.
ASTFlattener: Convertisseur d'AST Python en liste de nœuds aplatis.
ImportFromExtractor: Visiteur extrayant les noms importés via `from ... import`.
"""

from .director import ASTDirector
from .ast_builder import ASTBuilder
from .qt_ast_builder import QtASTBuilder
from .factory import BuilderFactory
from .flattener import ASTFlattener
from .vqt import ImportFromExtractor

__all__ = ["ASTDirector", "ASTBuilder", "QtASTBuilder", "BuilderFactory", "ASTFlattener", "ImportFromExtractor"]
