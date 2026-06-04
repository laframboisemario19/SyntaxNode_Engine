"""
Utilitaire d'organisation des métadonnées pour le moteur SyntaxNode.

Ce module fournit la classe `MetadataOrganizer`, qui restructure un dictionnaire
plat de métadonnées en une hiérarchie arborescente en exploitant les relations
parent-enfant présentes dans les données.

Classes
-------
MetadataOrganizer: Utilitaire statique de restructuration hiérarchique des métadonnées.
"""

from typing import Any, Dict
import copy


class MetadataOrganizer:
    """
    Utilitaire statique de restructuration hiérarchique des métadonnées.

    Transforme un dictionnaire plat de composants en une arborescence imbriquée
    en utilisant une clé désignant le parent de chaque élément. Les éléments
    sans parent identifiable dans le dictionnaire deviennent les racines de
    l'arbre résultant.
    """

    @staticmethod
    def organize_dict(dict_to_organize: Dict[Any, Any], key_word: str) -> Dict[Any, Any]:
        """
        Restructure un dictionnaire plat en une hiérarchie imbriquée.

        Utilise `key_word` pour identifier la relation parent-enfant de chaque
        entrée. Les entrées dont le parent n'existe pas dans le dictionnaire
        deviennent les racines de la hiérarchie résultante. Les données
        originales ne sont pas modifiées (deep copy).

        Args:
            dict_to_organize (Dict[Any, Any]): Le dictionnaire plat à restructurer.
                Chaque valeur peut contenir la clé `key_word` pointant vers
                le nom de son parent.
            key_word (str): Le nom de la clé désignant le parent d'un élément
                (ex: 'direct_parent').

        Returns:
            Dict[Any, Any]: Un dictionnaire hiérarchique où chaque entrée
                contient une clé 'children' regroupant ses enfants directs.
                Seules les racines (éléments sans parent dans le dictionnaire)
                apparaissent au niveau supérieur.
        """
        working_data = copy.deepcopy(dict_to_organize)
        root_objects = []

        for data in working_data.values():
            data["children"] = {}

        for name, data in working_data.items():
            parent_name = data.get(key_word)

            if parent_name and parent_name in working_data:
                working_data[parent_name]["children"][name] = data
            else:
                root_objects.append(name)

        for data in working_data.values():
            if key_word in data:
                del data[key_word]

        return {name: working_data[name] for name in root_objects}
