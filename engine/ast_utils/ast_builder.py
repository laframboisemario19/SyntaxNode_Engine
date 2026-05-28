"""
Interface abstraite pour la construction d'arbres syntaxiques (AST).

Ce module définit le contrat que tout constructeur d'AST spécifique à une
bibliothèque graphique doit respecter pour être utilisable par l'`ASTDirector`.

Classes
-------
ASTBuilder: Contrat abstrait pour la construction d'un AST Python.
"""

from abc import ABC, abstractmethod
from pathlib import Path
import ast
from typing import Self, Dict, Any, List

DEBUG_AST_PATH = Path(__file__).parent.parent.parent / "data" / "debug_ast.txt"

class ASTBuilder(ABC):
    """
    Contrat abstrait pour la construction d'un AST Python.

    Définit les étapes de construction nécessaires pour générer un arbre
    syntaxique complet à partir du graphe nodal. Toute nouvelle implémentation
    spécifique à une bibliothèque graphique (ex: Qt, Tkinter) doit hériter
    de cette classe et implémenter ses méthodes abstraites pour être
    utilisable par l'`ASTDirector`.

    Notes:
        Les méthodes `print_tree` et `fix_locations` sont des utilitaires
        communs à toutes les implémentations et ne sont donc pas abstraites.
    """

    @property
    @abstractmethod
    def tree(self:Self) -> ast.Module:
        """
        L'arbre syntaxique en cours de construction.

        Returns:
            ast.Module: Le nœud racine de l'AST courant.
        """
        pass
    
    @abstractmethod
    def reset(self: Self) -> None:
        """Réinitialise le constructeur pour permettre la construction d'un nouvel AST."""
        pass
    
    @abstractmethod
    def create_tree(self:Self, data:List[Dict[str, Any]]) -> None:
        """Initialise la structure racine de l'AST."""
        pass
    
    @abstractmethod
    def get_ast(self:Self) -> ast.Module:
        """
        Retourne l'AST complet et corrige les emplacements manquants.

        Returns:
            ast.Module: L'arbre syntaxique finalisé et prêt à être utilisé.
        """
        pass

    @abstractmethod
    def build_import(self:Self, data:List[Dict[str, Any]]) -> None:
        """
        Construit et ajoute les nœuds d'importation à l'AST.

        Args:
            data: Les données du graphe nodal nécessaires à la génération des imports.
        """
        pass

    @abstractmethod
    def build_class(self:Self, data:List[Dict[str, Any]], data_dict:Dict[str, Any]) -> None:
        """
        Construit et ajoute les nœuds de définition de classe à l'AST.

        Args:
            data: Les données du graphe nodal nécessaires à la génération des classes.
        """
        pass

    @abstractmethod
    def build_main(self:Self, data_dict:Dict[str, Any]) -> None:
        """
        Construit et ajoute la fonction principale et le bloc `if __name__ == "__main__"`.

        Args:
            data_dict: Le dictionnaire des composants nécessaires à la génération du main.
        """
        pass

    @abstractmethod
    def _find_root(self:Self, data:List[Dict[str, Any]]) -> str:
        """
        Identifie le composant racine du graphe nodal.

        Args:
            data: Les données du graphe nodal à analyser.

        Returns:
            str: L'identifiant du composant racine.
        """
        pass

    def print_tree(self:Self) -> None:
        """
        Écrit une représentation textuelle de l'AST dans un fichier de débogage.

        Sérialise l'AST courant avec indentation et le sauvegarde dans
        `../../data/debug_ast.txt` pour faciliter le débogage.
        """
        tree = ast.dump(self._tree, indent=4)

        with open(DEBUG_AST_PATH, mode="w", encoding="utf-8") as f:
            f.write(tree)

    def fix_locations(self:Self) -> None:
        """
        Corrige les emplacements manquants dans l'AST.

        Appelle `ast.fix_missing_locations` pour s'assurer que tous les nœuds
        de l'AST possèdent les attributs `lineno` et `col_offset` requis par
        le compilateur Python.
        """
        ast.fix_missing_locations(self._tree)