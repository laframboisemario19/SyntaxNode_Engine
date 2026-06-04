"""
Utilitaires de sérialisation et de transformation des métadonnées.

Ce module fournit la classe `MetadataSerializer`, qui regroupe les méthodes
utilitaires de transformation de noms, de nettoyage de types C++, de
restructuration de dictionnaires et de préparation des données pour la
génération de code.

Classes
-------
MetadataSerializer: Utilitaire statique de sérialisation et de transformation des métadonnées.
"""

import re
from typing import Any, Dict, List
import copy


class MetadataSerializer:
    """
    Utilitaire statique de sérialisation et de transformation des métadonnées.

    Regroupe les méthodes de transformation nécessaires à la conversion des
    métadonnées brutes (issues de l'introspection Qt) vers les formats attendus
    par le frontend SyntaxNode et le générateur d'AST.
    """

    @staticmethod
    def to_snake_case(text: str) -> str:
        """
        Convertit une chaîne CamelCase en snake_case.

        Args:
            text (str): La chaîne à convertir (ex: 'objectName').

        Returns:
            str: La chaîne en snake_case (ex: 'object_name').
        """
        ## Pour la regex : https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
        return re.sub(r'(?<!^)(?=[A-Z])', '_', text).lower()

    @staticmethod
    def clean_cpp_params(text: str) -> str:
        """
        Supprime les modificateurs de pointeur et de référence C++ d'un nom de type.

        Args:
            text (str): Le nom de type C++ à nettoyer (ex: 'QString*', 'QObject&').

        Returns:
            str: Le nom de type sans les caractères `*` et `&` (ex: 'QString').
        """
        return re.sub(r'[*&]', '', text)

    @staticmethod
    def restructure_dict(data: Any) -> Dict[str, List[Any]]:
        """
        Restructure le dictionnaire hiérarchique en une liste de nœuds sérialisés.

        Transforme la structure arborescente produite par `MetadataOrganizer`
        en une structure plate `{"core": [...]}` où chaque nœud est traité
        par `_process_node`. Les données originales ne sont pas modifiées (deep copy).

        Args:
            data (Any): Le dictionnaire hiérarchique à restructurer.

        Returns:
            Dict[str, List[Any]]: Un dictionnaire avec une unique clé 'core'
                contenant la liste des nœuds sérialisés.
        """
        working_data = copy.deepcopy(data)
        core_list = [MetadataSerializer._process_node(content) for content in working_data.values()]
        return {"core": core_list}

    @classmethod
    def sanitize_properties(cls, data: Dict[str, Any], metadata: Dict[str, Any]) -> None:
        """
        Filtre les propriétés dont la valeur est identique à la valeur par défaut.

        Pour chaque composant, compare la valeur de chaque propriété avec sa
        valeur par défaut dans les métadonnées et supprime celles qui n'ont
        pas été modifiées par l'utilisateur, afin d'alléger le code généré.

        Args:
            data (Dict[str, Any]): La liste des composants du graphe nodal
                à nettoyer (modifiée sur place).
            metadata (Dict[str, Any]): Les métadonnées de la bibliothèque
                contenant les valeurs par défaut des propriétés.
        """
        for component in data:
            comp_type = component["type"]
            comp_type = comp_type if component["category"] != "custom" else component["inheritance"][0]["type"]
            meta_properties = metadata[comp_type]["property"]

            cleaned_properties = []

            for prop in component["properties"]:
                prop_name = prop["name"]
                prop_value = prop["value"]
                keep_property = True

                if isinstance(prop_value, str):
                    if meta_properties[prop_name]["default"] == prop_value:
                        keep_property = False

                elif isinstance(prop_value, list):
                    for param in prop_value:
                        param_name = param["name"]
                        param_value = param["value"]
                        if meta_properties[prop_name]["value"][param_name]["default"] == param_value:
                            keep_property = False
                            break

                if keep_property:
                    cleaned_properties.append(prop)

            component["property"] = cleaned_properties

    @classmethod
    def _process_node(cls, node: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transforme récursivement un nœud de la hiérarchie en structure sérialisée.

        Convertit les sous-dictionnaires 'children', 'property' et 'method'
        en listes via `map_to_list`, et traite récursivement chaque enfant.

        Args:
            node (Dict[str, Any]): Le nœud de la hiérarchie à transformer.

        Returns:
            Dict[str, Any]: Le nœud transformé avec ses sous-structures sérialisées.
        """
        if not isinstance(node, dict):
            return node

        if "children" in node and isinstance(node["children"], dict):
            node["children"] = [cls._process_node(c) for c in node["children"].values()]

        if "property" in node and isinstance(node["property"], dict):
            node["property"] = cls.map_to_list(node["property"])

            for prop in node["property"]:
                if "value" in prop and isinstance(prop["value"], dict):
                    prop["value"] = cls.map_to_list(prop["value"])

        if "method" in node and isinstance(node["method"], dict):
            for m_type in ["signal", "slot"]:
                if m_type in node["method"] and isinstance(node["method"][m_type], dict):
                    node["method"][m_type] = cls.map_to_list(node["method"][m_type])

        return node

    @staticmethod
    def map_to_list(mapping: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Convertit un dictionnaire en liste de dictionnaires avec clé 'name'.

        Pour chaque entrée, si la valeur est un dictionnaire, injecte le nom
        de la clé sous 'name' si absent, puis ajoute le dictionnaire à la liste.
        Si la valeur n'est pas un dictionnaire, crée `{"name": clé, "value": valeur}`.

        Args:
            mapping (Dict[str, Any]): Le dictionnaire à convertir.

        Returns:
            List[Dict[str, Any]]: La liste des entrées converties.
        """
        result = []
        for key, value in mapping.items():
            if isinstance(value, dict):
                if "name" not in value:
                    value["name"] = key
                result.append(value)
            else:
                result.append({"name": key, "value": value})
        return result

    @staticmethod
    def list_to_map(listing: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Construit un dictionnaire indexé par identifiant à partir d'une liste de composants.

        Parcourt récursivement la liste pour indexer chaque nœud possédant un
        champ 'id' et rattache à chaque nœud l'identifiant de son parent via
        'parent_id'.

        Args:
            listing (List[Dict[str, Any]]): La liste de composants à indexer.

        Returns:
            Dict[str, Any]: Un dictionnaire associant chaque identifiant de
                composant à son dictionnaire de données, enrichi du champ
                'parent_id' pour les nœuds non racines.
        """
        result = {}

        def _recursive(node: Any, current_parent_id: str = None) -> None:
            if isinstance(node, dict):
                node_id = node.get("id")
                if node_id:
                    result[node_id] = node
                    if current_parent_id:
                        node["parent_id"] = current_parent_id
                    next_parent = node_id
                else:
                    next_parent = current_parent_id
                for value in node.values():
                    _recursive(value, next_parent)

            elif isinstance(node, list):
                for item in node:
                    _recursive(item, current_parent_id)

        _recursive(listing)
        return result
