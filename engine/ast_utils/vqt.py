"""
Visiteurs d'AST utilitaires pour le moteur SyntaxNode.

Ce module fournit des visiteurs d'AST spécialisés utilisés lors de la
construction des jeux de données d'entraînement pour les modèles PyTorch.

Classes
-------
ImportFromExtractor: Visiteur extrayant les noms importés via `from ... import`.
"""

import ast
from typing import Self, List, override


class ImportFromExtractor(ast.NodeVisitor):
    """
    Visiteur extrayant les noms importés via des instructions `from ... import`.

    Parcourt l'AST et collecte les noms des symboles importés, en excluant
    les features PySide6 (`true_property`, `snake_case`) qui sont des
    directives de compilateur et non des symboles Python standards.

    Attributes:
        _import_list (List[str]): La liste des noms de symboles importés
            collectés lors de la dernière traversée.
    """

    def __init__(self: Self) -> None:
        """Initialise le visiteur avec une liste d'imports vide."""
        self._import_list: List[str] = []

    @override
    def generic_visit(self: Self, node: ast.AST) -> List[str]:
        """
        Visite un nœud générique, réinitialise la liste et visite ses enfants.

        Réinitialise `_import_list` à chaque appel pour permettre une
        utilisation répétée du visiteur sur plusieurs arbres.

        Args:
            node (ast.AST): Le nœud racine à visiter.

        Returns:
            List[str]: La liste des noms de symboles importés trouvés.
        """
        self._import_list = []
        super().generic_visit(node)
        return self._import_list

    @override
    def visit_ImportFrom(self: Self, node: ast.ImportFrom) -> None:
        """
        Visite un nœud `from ... import` et collecte les noms importés.

        Exclut les features PySide6 (`true_property`, `snake_case`) qui
        sont des directives internes et non des symboles Python standards.

        Args:
            node (ast.ImportFrom): Le nœud d'importation à visiter.
        """
        for alias in node.names:
            name = alias.name
            if name not in ("true_property", "snake_case"):
                self._import_list.append(alias.name)
        self.generic_visit(node)
