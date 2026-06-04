"""
Générateur de code source et d'archives pour le moteur SyntaxNode.

Ce module fournit la classe `CodeGenerator`, qui transforme un arbre
syntaxique Python (ast.Module) en code source formaté et compresse les
fichiers générés dans une archive ZIP en mémoire.

Classes
-------
CodeGenerator: Utilitaire statique de génération de code source et d'archives ZIP.
"""

import zipfile
import ast
from io import BytesIO
from typing import Tuple


class CodeGenerator():
    """
    Utilitaire statique de génération de code source et d'archives ZIP.

    Transforme un AST Python en code source, applique les transformations
    nécessaires (ex: ajout des annotations de features PySide6), puis
    compresse les fichiers générés dans une archive ZIP retournée en mémoire.
    """

    @classmethod
    def generate_code(cls, tree: ast.Module) -> str:
        """
        Génère le code source Python à partir d'un arbre syntaxique.

        Sérialise l'AST en code source via `ast.unparse`, puis applique
        les transformations de post-traitement via `_add_features`.

        Args:
            tree (ast.Module): L'arbre syntaxique à convertir en code source.

        Returns:
            str: Le code source Python formaté et prêt à être écrit dans un fichier.
        """
        code = ast.unparse(tree)
        return cls._add_features(code)

    @staticmethod
    def generate_file(file_name: str, code: str) -> Tuple[str, str]:
        """
        Crée un tuple représentant un fichier à inclure dans l'archive.

        Args:
            file_name (str): Le nom du fichier (ex: 'main_application.py').
            code (str): Le contenu du fichier.

        Returns:
            Tuple[str, str]: Un tuple (nom_fichier, contenu) prêt à être
                passé à `generate_zip_files`.
        """
        return (file_name, code)

    ## Source : https://blog.finxter.com/5-best-ways-to-write-bytes-to-a-zip-file-using-python/
    @staticmethod
    def generate_zip_files(files: Tuple[Tuple[str, str], ...]) -> BytesIO:
        """
        Compresse une collection de fichiers dans une archive ZIP en mémoire.

        Args:
            files (Tuple[Tuple[str, str], ...]): Un tuple de tuples (nom, contenu)
                représentant les fichiers à compresser.

        Returns:
            BytesIO: Un flux de données en mémoire contenant l'archive ZIP,
                positionné au début et prêt à être lu ou expédié.
        """
        buffer = BytesIO()
        with zipfile.ZipFile(buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            for f in files:
                name, data = f
                zip_file.writestr(name, data)

        buffer.seek(0)
        return buffer

    @classmethod
    def _add_features(cls, code: str) -> str:
        """
        Applique les transformations de post-traitement au code source généré.

        Méthode interne servant de point d'extension pour les transformations
        globales du code. Actuellement délègue à `_snakecase_and_trueproperty`.

        Args:
            code (str): Le code source brut généré par `ast.unparse`.

        Returns:
            str: Le code source après application des transformations.
        """
        return cls._snakecase_and_trueproperty(code)

    @staticmethod
    def _snakecase_and_trueproperty(code: str) -> str:
        """
        Ajoute l'annotation `type: ignore` aux imports de features PySide6.

        Les imports `from __feature__ import` génèrent des avertissements de
        type dans les éditeurs car `__feature__` n'est pas un module Python
        standard. Cette méthode ajoute le commentaire `#type: ignore` pour
        les supprimer.

        Args:
            code (str): Le code source à transformer.

        Returns:
            str: Le code source avec les annotations `type: ignore` ajoutées.
        """
        target_line1 = "from __feature__ import true_property, snake_case"
        target_line2 = "from __feature__ import snake_case, true_property"

        modified_line = target_line1 + " #type: ignore[import-not-found]"
        source_code = code.replace(target_line1, modified_line)
        modified_line = target_line2 + " #type: ignore[import-not-found]"
        source_code = source_code.replace(target_line2, modified_line)

        return source_code
