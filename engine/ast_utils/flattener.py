"""
Sérialiseur d'AST Python en structure aplatie.

Ce module fournit la classe `ASTFlattener`, qui transforme un arbre syntaxique
Python (ast.AST) en une liste de nœuds aplatis. Cette représentation linéaire
est utilisée comme entrée pour les modèles PyTorch d'analyse statique.

Classes
-------
ASTFlattener: Convertisseur d'AST en liste de nœuds aplatis.
"""

from __future__ import annotations

from typing import Self, Any, List, Tuple, Optional
import ast


class ASTFlattener():
    """
    Convertisseur d'AST Python en liste de nœuds aplatis.

    Transforme un arbre syntaxique Python en une liste de nœuds où chaque
    nœud est représenté par son type, son identifiant parent, ses enfants
    et sa valeur littérale. Cette représentation est utilisée comme entrée
    pour les modèles PyTorch d'analyse statique.

    Attributes:
        flatten_tree (List): La liste aplatie des nœuds produite lors de
            la dernière invocation de `flatten`.
    """

    def __init__(self: Self) -> None:
        """Initialise le convertisseur avec une liste de nœuds vide."""
        self.flatten_tree: List[List[Any]] = []

    def flatten(self: Self, tree: ast.AST) -> List[List[Any]]:
        """
        Transforme un arbre syntaxique en une liste de nœuds aplatis.

        Réinitialise la liste interne puis parcourt récursivement l'AST
        pour construire la représentation aplatie.

        Args:
            tree (ast.AST): L'arbre syntaxique à aplatir.

        Returns:
            List[List[Any]]: La liste aplatie des nœuds. Chaque nœud est
                représenté par `[type, parent_id, children_ids, value]`.
        """
        self.flatten_tree = []
        self._traverse(tree, None, "Module")
        return self.flatten_tree

    def _add_node(self: Self, type: str, parent_id: Optional[int], value: str | int | float | bool = "") -> int:
        """
        Ajoute un nœud à la liste aplatie et met à jour les liens parent-enfant.

        Méthode interne appelée par `_traverse`. Chaque nœud est représenté
        par `[type, parent_id, children_ids, value]`. Le nœud racine a
        `parent_id = -1`.

        Args:
            type (str): Le type du nœud (ex: 'AST_Module', 'AST_value').
            parent_id (Optional[int]): L'indice du nœud parent dans la liste,
                ou None pour le nœud racine.
            value (str | int | float | bool): La valeur littérale du nœud,
                si applicable.

        Returns:
            int: L'indice du nœud nouvellement ajouté dans la liste aplatie.
        """
        node_id = len(self.flatten_tree)
        parent_id = parent_id if parent_id is not None else -1
        self.flatten_tree.append([type, parent_id, [], value])

        if parent_id != -1:
            self.flatten_tree[parent_id][2].append(node_id)

        return node_id

    def _traverse(self: Self, obj: ast.AST | List[Any], parent_id: Optional[int], obj_type: str) -> None:
        """
        Parcourt récursivement l'AST et peuple la liste aplatie.

        Méthode interne appelée par `flatten`. Distingue trois cas :
        les nœuds AST (récursion sur les champs), les listes (récursion sur
        chaque élément) et les valeurs terminales (ajout direct).

        Args:
            obj (ast.AST | List[Any]): L'objet courant à parcourir.
            parent_id (Optional[int]): L'indice du nœud parent dans la liste.
            obj_type (str): Le type ou le nom du champ du nœud courant.
        """
        if isinstance(obj, ast.AST):
            node_type = f"AST_{obj.__class__.__name__}"
            current_id = self._add_node(node_type, parent_id)

            for fieldname, value in ast.iter_fields(obj):
                self._traverse(value, current_id, fieldname)

        elif isinstance(obj, list):
            if obj:
                for item in obj:
                    self._traverse(item, parent_id, obj_type)

        elif obj is not None or (obj is None and obj_type == "value"):
            self._add_node(f"AST_{obj_type}", parent_id, obj)
