"""
Directeur d'AST pour le moteur SyntaxNode.

Ce module fournit la classe `ASTDirector`, qui orchestre la séquence de
construction d'un arbre syntaxique Python en déléguant chaque étape au
constructeur (`ASTBuilder`) configuré. Il gère également la réorganisation
des données pour la génération d'aperçus visuels.

Classes
-------
ASTDirector: Orchestrateur de la construction d'un AST à partir d'un graphe nodal.
"""

from typing import Self, List, Dict, Any, Optional

from .ast_builder import ASTBuilder
from ..utils import MetadataSerializer as mds


class ASTDirector():
    """
    Orchestrateur de la construction d'un AST à partir d'un graphe nodal.

    Coordonne la séquence de construction de l'AST en délégant chaque étape
    (imports, classes, main) au constructeur configuré. Gère également la
    réorganisation temporaire des données du graphe nodal lors de la génération
    d'aperçus visuels pour un composant cible spécifique.

    Attributes:
        _builder (ASTBuilder): Le constructeur d'AST actif.
        _ast_validator (ASTValidator): Le validateur d'AST partagé avec le constructeur.
    """

    def __init__(self, builder: ASTBuilder) -> None:
        """
        Initialise le directeur avec un constructeur d'AST.

        Args:
            builder (ASTBuilder): Le constructeur à utiliser pour la génération
                de l'arbre syntaxique.
        """
        self._builder = builder
        self._ast_validator = builder._ast_validator

    def change_builder(self, builder: ASTBuilder) -> None:
        """
        Remplace le constructeur d'AST actif.

        Args:
            builder (ASTBuilder): Le nouveau constructeur à utiliser pour les
                prochains appels à `make`.
        """
        self._builder = builder
        self._ast_validator = builder._ast_validator

    def make(self, data: List[Dict[str, Any]], metadata: Dict[str, Any], target_id: str = "") -> Any:
        """
        Orchestre la construction complète d'un AST à partir d'un graphe nodal.

        Nettoie les propriétés redondantes, construit les imports, les classes
        et le main, puis valide l'AST si aucun `target_id` n'est spécifié.
        Si `target_id` est fourni, réorganise les données pour générer un AST
        partiel centré sur le composant cible.

        Args:
            data (List[Dict[str, Any]]): La liste contenant le dictionnaire du
                projet SyntaxNode.
            metadata (Dict[str, Any]): Les métadonnées de la bibliothèque
                graphique cible.
            target_id (str): L'identifiant du composant cible pour la génération
                d'un aperçu visuel. Si vide, génère l'AST complet.

        Returns:
            ast.Module: L'arbre syntaxique Python finalisé.
        """
        data = data[0]
        mds.sanitize_properties(data["components"], metadata)

        self._builder.reset()
        self._builder.create_tree(data)

        data_dict = mds.list_to_map(data["components"])

        root_list = self._builder._find_root(data["components"])

        if target_id:
            self._rearrange_data(target_id, data_dict, data["components"], root_list[0])
            self._builder._find_root(data["components"])
            data["links"] = []

        self._builder.build_import(data["components"])
        self._builder.build_class(data, data_dict)
        self._builder.build_main(data_dict)
        self._builder.fix_locations()

        self._builder.print_tree()

        tree = self._builder.get_ast()

        if not target_id:
            self._ast_validator.validate_data(tree)

        return tree

    def validate_ast(self: Self, tree: Any) -> None:
        """
        Valide un arbre syntaxique déjà construit.

        Args:
            tree (ast.AST): L'arbre syntaxique à valider.
        """
        self._ast_validator.validate_ast(tree)

    def _rearrange_data(self: Self, target_id: str, data_dict: Dict[str, Any], components: List[Dict[str, Any]], root_id: str) -> None:
        """
        Réorganise les données du graphe pour centrer l'AST sur un composant cible.

        Détermine la catégorie du composant cible et de son parent, puis applique
        la réorganisation appropriée pour que le widget `MyApp` soit le contenant
        direct du composant à prévisualiser.

        Args:
            target_id (str): L'identifiant du composant cible.
            data_dict (Dict[str, Any]): Le dictionnaire des composants indexés
                par identifiant.
            components (List[Dict[str, Any]]): La liste des composants du graphe.
            root_id (str): L'identifiant du composant racine original.
        """
        parent_id = self._find_parent(target_id, components)
        parent = data_dict.get(parent_id, None)
        if parent:
            parent_category = parent["category"]
            parent_category = parent.get("inheritance", {})[0].get("type", "widget") if parent_category == "custom" else parent_category

        grand_parent = self._find_parent(parent_id, components)

        target = data_dict.get(target_id, {})
        target_category = target.get("category", None)
        target_category = target.get("inheritance", {})[0].get("type", "widget") if target_category == "custom" else target_category

        root = data_dict[root_id]
        root["type"] = "MyApp"

        if target_category == "layout" and parent_category == "widget":
            self._replace_parent_widget(parent, grand_parent, target, components, data_dict, root)
        elif target_category == "layout" and parent_category == "layout":
            self._add_parent_widget(parent, target, components, data_dict, root)
        elif target_category == "widget":
            self._rearrange_target_widget(target, parent, components, data_dict, root)

    def _replace_parent_widget(self: Self, parent: Dict[str, Any], grand_parent: Optional[str], target: Dict[str, Any], components: List[Dict[str, Any]], data_dict: Dict[str, Any], root: Dict[str, Any]) -> None:
        """
        Remplace le widget parent par un widget `my_widget` contenant le layout cible.

        Utilisé quand le composant cible est un layout enfant d'un widget.
        Remplace le parent dans la hiérarchie par un nouveau widget `my_widget`
        qui conserve ses propriétés, variables et enfants.

        Args:
            parent (Dict[str, Any]): Le composant parent à remplacer.
            grand_parent (Optional[str]): L'identifiant du grand-parent du parent,
                ou None si le parent est la racine.
            target (Dict[str, Any]): Le composant cible de l'aperçu.
            components (List[Dict[str, Any]]): La liste des composants du graphe.
            data_dict (Dict[str, Any]): Le dictionnaire des composants indexés
                par identifiant.
            root (Dict[str, Any]): Le composant racine de l'arbre.
        """
        inheritance = []
        w_type = "QWidget"
        if parent == root:
            inheritance = [{"type": "QWidget", "module": "PySide6.QtWidgets"}]
            w_type = "MyApp"

        variable = parent["variable"]
        properties = parent["properties"]
        child = parent["child"]

        widget = {"id": "my_widget",
                  "type": w_type,
                  "category": "widget",
                  "name": "my_widget",
                  "variable": variable,
                  "inheritance": inheritance,
                  "child": child,
                  "properties": properties,
                  "function": []
                  }

        components.append(widget)
        components.remove(parent)
        data_dict["my_widget"] = widget
        data_dict.pop(parent["id"])

        if grand_parent:
            data_dict[grand_parent]["child"].remove(parent["id"])
            data_dict[grand_parent]["child"].append(widget["id"])

        id_in_variable = [var["value"]["value"] for var in root["variable"]]
        if target["id"] not in id_in_variable and parent != root:
            variable = {
                "id": "my_widget",
                "name": "my_widget",
                "value": {"type": "id", "value": "my_widget"},
                "scope": "public",
            }
            root["variable"].append(variable)

    def _add_parent_widget(self: Self, parent: Dict[str, Any], target: Dict[str, Any], components: List[Dict[str, Any]], data_dict: Dict[str, Any], root: Dict[str, Any]) -> None:
        """
        Insère un widget `my_widget` comme parent direct du layout cible.

        Utilisé quand le composant cible est un layout enfant d'un autre layout.
        Insère un QWidget intermédiaire pour respecter la règle Qt qui exige
        qu'un widget soit le conteneur d'un layout.

        Args:
            parent (Dict[str, Any]): Le composant parent actuel du layout cible.
            target (Dict[str, Any]): Le composant cible de l'aperçu (layout).
            components (List[Dict[str, Any]]): La liste des composants du graphe.
            data_dict (Dict[str, Any]): Le dictionnaire des composants indexés
                par identifiant.
            root (Dict[str, Any]): Le composant racine de l'arbre.
        """
        widget = {"id": "my_widget",
                  "type": "QWidget",
                  "category": "widget",
                  "name": "my_widget",
                  "variable": [],
                  "inheritance": [],
                  "child": [target["id"]],
                  "properties": [],
                  "function": []
                  }

        parent["child"].remove(target["id"])
        parent["child"].append(widget["id"])
        components.append(widget)
        data_dict["my_widget"] = widget

        id_in_variable = [var["id"] for var in root["variable"]]
        if target["id"] not in id_in_variable:
            variable = {
                "id": "my_widget",
                "name": "my_widget",
                "value": {"type": "id", "value": "my_widget"},
                "scope": "public",
            }
            root["variable"].append(variable)

    def _rearrange_target_widget(self: Self, target: Dict[str, Any], parent: Dict[str, Any], components: List[Dict[str, Any]], data_dict: Dict[str, Any], root: Dict[str, Any]) -> None:
        """
        Renomme le widget cible en `my_widget` pour l'aperçu visuel.

        Si le widget cible est la racine, ne fait rien. Sinon, renomme le
        composant et ajoute ou met à jour la variable correspondante dans
        le composant racine.

        Args:
            target (Dict[str, Any]): Le composant widget cible de l'aperçu.
            parent (Dict[str, Any]): Le composant parent du widget cible.
            components (List[Dict[str, Any]]): La liste des composants du graphe.
            data_dict (Dict[str, Any]): Le dictionnaire des composants indexés
                par identifiant.
            root (Dict[str, Any]): Le composant racine de l'arbre.
        """
        if target["id"] == root["id"]:
            return

        target["name"] = "my_widget"

        for var in root["variable"]:
            if target["id"] == var["value"]["value"]:
                var["name"] = "my_widget"
                return

        variable = {
            "id": "my_widget",
            "name": "my_widget",
            "value": {"type": "id", "value": target["id"]},
            "scope": "public",
        }
        root["variable"].append(variable)

    def _find_parent(self: Self, target_id: str, data: List[Dict[str, Any]]) -> Optional[str]:
        """
        Trouve l'identifiant du composant parent d'un composant donné.

        Parcourt la liste des composants pour trouver celui dont la liste
        d'enfants contient `target_id`.

        Args:
            target_id (str): L'identifiant du composant dont on cherche le parent.
            data (List[Dict[str, Any]]): La liste des composants du graphe.

        Returns:
            Optional[str]: L'identifiant du composant parent, ou None si le
                composant n'a pas de parent (racine).
        """
        for c in data:
            for child_id in c["child"]:
                if child_id == target_id:
                    return c["id"]

    def _add_root_widget(self: Self, root_variables: List[Dict[str, Any]], root_properties: List[Dict[str, Any]], child_id: str, widget_id: str) -> Dict[str, Any]:
        """
        Crée un dictionnaire représentant un widget racine de type `MyApp`.

        Méthode utilitaire pour construire la structure d'un composant racine
        QWidget héritant de MyApp, à utiliser lors de la réorganisation des données.

        Args:
            root_variables (List[Dict[str, Any]]): Les variables du composant racine.
            root_properties (List[Dict[str, Any]]): Les propriétés du composant racine.
            child_id (str): L'identifiant de l'enfant direct du widget racine.
            widget_id (str): L'identifiant à assigner au nouveau widget racine.

        Returns:
            Dict[str, Any]: Le dictionnaire représentant le composant racine créé.
        """
        variables = root_variables
        children = [child_id]
        properties = root_properties
        inheritance = [{"type": "QWidget", "module": "PySide6.QtWidgets"}]

        application = {"id": widget_id,
                       "type": "MyApp",
                       "category": "core",
                       "name": "app",
                       "variable": variables,
                       "inheritance": inheritance,
                       "child": children,
                       "properties": properties,
                       "function": []
                       }

        return application

    def _add_components(self: Self, target_id: str, data_dict: Dict[str, Any], new_components: List[Dict[str, Any]], new_data_dict: Dict[str, Any]) -> None:
        """
        Copie récursivement un composant et ses enfants dans de nouvelles structures.

        Parcourt le sous-arbre enraciné à `target_id` et copie chaque composant
        rencontré dans `new_components` et `new_data_dict`.

        Args:
            target_id (str): L'identifiant du composant racine à copier.
            data_dict (Dict[str, Any]): Le dictionnaire source des composants.
            new_components (List[Dict[str, Any]]): La liste de destination.
            new_data_dict (Dict[str, Any]): Le dictionnaire de destination.
        """
        comp = data_dict[target_id]
        new_components.append(comp)
        new_data_dict[target_id] = comp

        children = comp.get("child")

        if children:
            for c in children:
                self._add_components(c, data_dict, new_components, new_data_dict)
