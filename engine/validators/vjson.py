"""
Validation du schéma JSON pour le moteur SyntaxNode.

Ce module définit les modèles Pydantic représentant la structure d'un projet
SyntaxNode ainsi que la classe `JsonValidator`, qui orchestre la validation
du schéma, des références et de la structure du graphe nodal.

Classes
-------
Project: Modèle Pydantic représentant la structure complète d'un projet.
Component: Modèle Pydantic représentant un composant du graphe nodal.
Link: Modèle Pydantic représentant une connexion entre deux composants.
Variable: Modèle Pydantic représentant une variable d'un composant.
Function: Modèle Pydantic représentant une fonction utilisateur d'un composant.
InternFunction: Modèle Pydantic représentant une fonction interne d'un composant.
Properties: Modèle Pydantic représentant une propriété de type primitif.
EnumProperties: Modèle Pydantic représentant une propriété de type énumération.
FlagProperties: Modèle Pydantic représentant une propriété de type flag.
ObjectProperties: Modèle Pydantic représentant une propriété de type objet.
Inheritance: Modèle Pydantic représentant l'héritage d'un composant.
FlagValue: Modèle Pydantic représentant la valeur d'une propriété de type flag.
ObjectValue: Modèle Pydantic représentant la valeur d'une propriété de type objet.
Value: Modèle Pydantic représentant une valeur générique.
JsonValidator: Orchestrateur de la validation du schéma JSON d'un projet.
"""

from __future__ import annotations

from typing import List, Any, Optional, Literal, Dict, Set, Tuple
from ..error import *
from pydantic import BaseModel, ValidationError, field_validator

class InternFunction(BaseModel):
    """Modèle représentant une fonction interne générée automatiquement par le moteur."""
    id: str
    name: str
    is_intern: Literal[True]

class Function(BaseModel):
    """Modèle représentant une fonction définie par l'utilisateur dans un composant."""
    id: str
    name: str
    params: List[str]
    code: List[str]
    is_intern: Literal[False]

class Properties(BaseModel):
    """Modèle représentant une propriété de type primitif (int, str, float, bool)."""
    name: str
    type: Literal["int", "str", "float", "bool"]
    value: Optional[int | str | float | bool] = None

class EnumProperties(BaseModel):
    """Modèle représentant une propriété de type énumération Qt."""
    name: str
    type: Literal["enum"]
    namespace: List[str]
    value: str

class FlagProperties(BaseModel):
    """Modèle représentant une propriété de type flag Qt."""
    name: str
    type: Literal["flag"]
    namespace: List[str]
    value: FlagValue

class ObjectProperties(BaseModel):
    """Modèle représentant une propriété de type objet Qt complexe."""
    name: str
    type: str
    module: str
    value: List[ObjectValue]

class Inheritance(BaseModel):
    """Modèle représentant la classe parente d'un composant."""
    type: str
    module: str

class FlagValue(BaseModel):
    """Modèle représentant la valeur d'une propriété de type flag, avec des options exclusives et non exclusives."""
    exclusive: Dict[str, str]
    non_exclusive: List[str]

class ObjectValue(BaseModel):
    """Modèle représentant la valeur d'un argument d'une propriété de type objet."""
    type: str
    value: str | List[Value] | int | bool | float
    name: str

class Value(BaseModel):
    """Modèle représentant une valeur générique pouvant être primitive ou imbriquée."""
    type: str
    value: str | List[Value] | int | bool | float

class Variable(BaseModel):
    """Modèle représentant une variable d'un composant avec sa portée et sa valeur."""
    id: str
    name: str
    value: Value
    scope: Literal["public", "private"]

class Component(BaseModel):
    """Modèle représentant un composant du graphe nodal avec ses propriétés, variables et fonctions."""
    id: str
    type: str
    category: str
    name: str
    module: str
    child: List[str]
    variable: List[Variable]
    inheritance: List[Inheritance]
    properties:List[Properties | EnumProperties | FlagProperties | ObjectProperties]
    function: List[Function | InternFunction]

class Link(BaseModel):
    """Modèle représentant une connexion directionnelle entre deux composants du graphe nodal."""
    id: str
    source: str
    target: str
    type: str

class Project(BaseModel):
    """Modèle représentant la structure complète d'un projet SyntaxNode."""
    id_project:str
    id_owner:str
    last_update:str
    project_name:str
    components: List[Component]
    links: List[Link]

    @field_validator("components")
    @classmethod
    def validate_root_component(cls, components:List[Component]) -> List[Component]:
        """
        Valide la structure des composants racines du projet.

        Vérifie qu'il y a au moins un composant, que le premier est de catégorie
        `custom` et qu'aucun autre composant n'est de catégorie `custom`.

        Args:
            components (List[Component]): La liste des composants à valider.

        Returns:
            List[Component]: La liste des composants si la validation réussit.

        Raises:
            RootError: Si le projet n'a pas de composant, si le premier composant
                n'est pas de catégorie `custom`, ou si un autre composant est de
                catégorie `custom`.
        """
        if not components:
            raise RootError("Le projet doit avoir au minimum 1 composant.")
        if components[0].category != "custom":
            raise RootError("Le premier composant doit être de category custom.")
        
        for component in components[1:]:
            if component.category == "custom":
                raise RootError("Seul le premier composant peut être de category custom.")

        return components

class JsonValidator:
    """
    Orchestrateur de la validation du schéma JSON d'un projet SyntaxNode.

    Valide les données du graphe nodal en plusieurs étapes : conformité du
    schéma Pydantic, unicité des identifiants, validité des références,
    absence de dépendances circulaires et respect des règles structurelles Qt.

    Les algorithmes de validation sont regroupés en séquences dans `_algo_list`,
    où chaque séquence est exécutée entièrement avant de passer à la suivante —
    permettant un arrêt anticipé si des erreurs bloquantes sont détectées.
    """

    @staticmethod
    def validate_data(data: List[Dict[str, Any]]) -> bool:
        """
        Valide la conformité des données du projet SyntaxNode.

        Vérifie d'abord les types de base, puis valide le schéma complet via
        Pydantic et orchestre la validation structurelle via `_validate_data_structure`.

        Args:
            data (List[Dict[str, Any]]): La liste contenant le dictionnaire du projet
                à valider.

        Returns:
            bool: True si les données sont valides.

        Raises:
            TypeJsonFormatError: Si les données ne sont pas de type list ou si le
                projet n'est pas de type dict.
            JsonFormatError: Si les données ne respectent pas le schéma Pydantic.
            ErrorContainer: Si plusieurs groupes d'erreurs structurelles sont détectés.
        """
        if not isinstance(data, list):
            raise TypeJsonFormatError(f"Les données doivent être de type list et non de type {data.__class__.__name__}")
        
        project_data = data[0]
        if not isinstance(project_data, dict):
            raise TypeJsonFormatError(f"Les projets doivent être de type dict et non de type {project_data.__class__.__name__}")
        
        try:
            Project(**project_data) 
        except ValidationError as e:
            error_list = []
            for error_detail in e.errors():
                error_path = [str(loc) for loc in error_detail["loc"]]
                error_msg = error_detail["msg"]
                error_list.append(ErrorDetails(error_path, error_msg))
            raise JsonFormatError(error_list)
        
        JsonValidator._validate_data_structure(project_data)

        return True
    
    @staticmethod
    def _validate_data_structure(data: Dict[str, Any]) -> bool:
        """
        Orchestre l'exécution des algorithmes de validation structurelle.

        Méthode interne destinée à être appelée par `validate_data`. Extrait
        les identifiants et métadonnées nécessaires via `_extract_id`, puis
        exécute les séquences d'algorithmes de `_algo_list` en ordre. Si des
        erreurs sont détectées dans une séquence, elles sont regroupées dans
        un `ErrorContainer` et levées avant de passer à la séquence suivante.

        Args:
            data (Dict[str, Any]): Le dictionnaire du projet à valider.

        Returns:
            bool: True si la structure est valide.

        Raises:
            ErrorContainer: Si des erreurs structurelles sont détectées.
        """
        error_list = []
        
        keys = ("component_id", "components_loc", "components_dict", "variable_id", "variable_loc", "function_id", "function_loc", "link_id", "link_loc", "children_tree", "ref_variable_id", "ref_variable_loc")
        id_extracted = {key:data_extracted for key, data_extracted in zip(keys, JsonValidator._extract_id(data))}

        for algo_seq in JsonValidator._algo_list:
            for algo in algo_seq:
                error = algo(id_extracted)
                if error:
                    error_list.append(error)

            if error_list:
                raise ErrorContainer(error_list)

        return True
    
    @staticmethod
    def _extract_id(data: Dict[str, Any]) -> Tuple[List[str]]:
        """
        Extrait et organise les identifiants et métadonnées du projet.

        Méthode interne destinée à être appelée par `_validate_data_structure`.
        Parcourt l'ensemble des composants, variables, fonctions et liens pour
        construire les structures de données nécessaires aux algorithmes de
        validation.

        Args:
            data (Dict[str, Any]): Le dictionnaire du projet à analyser.

        Returns:
            Tuple[List[str]]: Un tuple contenant dans l'ordre : les identifiants
                des composants, leurs emplacements, leur dictionnaire, les
                identifiants des variables, leurs emplacements, les identifiants
                des fonctions, leurs emplacements, les identifiants des liens,
                leurs emplacements, l'arbre des enfants, les identifiants des
                variables référencées et leurs emplacements.
        """
        components_id = []
        components_loc = []
        components_dict = {}

        variable_id = []
        variable_loc = []

        function_id = []
        function_loc = []

        link_id = []
        link_loc = []

        children_tree = {}

        ref_variable_id = []
        ref_variable_loc = []

        for i, component in enumerate(data.get("components", [])):
            components_id.append(component["id"])
            loc = ["components", str(i), "id"]
            components_loc.append(loc)

            components_dict[component["id"]] = {"loc" : loc, "category": component["category"]}

            for j, variable in enumerate(component.get("variable", [])):
                variable_id.append(variable["id"])
                variable_loc.append(["components", str(i), "variable", str(j), "id"])

                value = variable["value"]
                if value["type"] == "id":
                    ref_variable_id.append(value["value"])
                    ref_variable_loc.append(["components", str(i), "variable", str(j), "value", "value"])

            children_tree[component["id"]] = []
            for m, child in enumerate(component.get("child", [])):
                children_tree[component["id"]].append({"child":child, "loc":["components", str(i), "child", str(m)]})

            for k, function in enumerate(component.get("function", [])):
                function_id.append(function["id"])
                function_loc.append(["components", str(i), "function", str(k), "id"])

        for l, link in enumerate(data.get("links", [])):
            link_id.append(link["source"])
            link_loc.append(["links", str(l), "source"])
            link_id.append(link["target"])
            link_loc.append(["links", str(l), "target"])

        return (components_id, components_loc, components_dict, variable_id, variable_loc, function_id, function_loc, link_id, link_loc, children_tree, ref_variable_id, ref_variable_loc)
    
    @staticmethod
    def _algo_unique_id(data:Dict[List[str]]) -> UniqueIdError | None:
        """
        Vérifie l'unicité de tous les identifiants du projet.

        Détecte les identifiants dupliqués parmi les composants, variables et
        fonctions, en indiquant pour chaque doublon l'emplacement du conflit
        et l'emplacement de la première occurrence.

        Args:
            data (Dict[List[str]]): Les identifiants et métadonnées extraits
                par `_extract_id`.

        Returns:
            UniqueIdError | None: Une exception contenant les erreurs détectées,
                ou None si tous les identifiants sont uniques.
        """
        all_id = data["component_id"] + data["variable_id"] + data["function_id"]
        all_location = data["components_loc"] + data["variable_loc"] + data["function_loc"]
        id_dict = {}
        error_list = []
        error = None

        for id_analysing, location in zip(all_id, all_location):
            if id_analysing not in id_dict:
                id_dict[id_analysing] = location
            else:
                error_path = location
                other_path = " -> ".join(id_dict[id_analysing])
                error_msg = f"id {id_analysing} également assigné à [{other_path}]"
                error_list.append(ErrorDetails(error_path, error_msg))

        if error_list:
            error = UniqueIdError(error_list)

        return error
    
    @staticmethod
    def _algo_reference(data:Dict[List[str]]) -> ReferenceError | None:
        """
        Vérifie que toutes les références pointent vers des identifiants existants.

        Détecte les références invalides dans les liens et les variables
        référencées, en vérifiant que chaque identifiant cible existe parmi
        les composants, variables et fonctions du projet.

        Args:
            data (Dict[List[str]]): Les identifiants et métadonnées extraits
                par `_extract_id`.

        Returns:
            ReferenceError | None: Une exception contenant les erreurs détectées,
                ou None si toutes les références sont valides.
        """
        all_id = data["component_id"] + data["variable_id"] + data["function_id"]
        link_id = data["link_id"] + data["ref_variable_id"]
        link_loc = data["link_loc"] + data["ref_variable_loc"]
        error_list = []
        error = None
    
        for id_analysing, location in zip(link_id, link_loc):
            if id_analysing not in all_id:
                error_path = location
                error_msg = f"id {id_analysing} inexistant dans le projet"
                error_list.append(ErrorDetails(error_path, error_msg))
        if error_list:
            error = ReferenceError(error_list)

        return error
    
    @staticmethod
    def _algo_circular_dependency(data:Dict[List[str]]) -> LinksError | None:
        """
        Détecte les dépendances circulaires et les composants déconnectés.

        Parcourt récursivement l'arbre des enfants à partir du composant racine
        pour détecter les cycles et identifier les composants non connectés au
        composant principal.

        Args:
            data (Dict[List[str]]): Les identifiants et métadonnées extraits
                par `_extract_id`.

        Returns:
            LinksError | None: Une exception contenant les erreurs détectées,
                ou None si le graphe est valide.
        """
        comps_id = data["component_id"]
        comps_loc = data["components_loc"]
        children_tree = data["children_tree"]
        error_details_list = []
        error = None
        sequences = set()

        def _recursive(children_tree, sequence, parent_id):
            children = children_tree[parent_id]
            if not children:
                return sequence
            
            for child in children:
                if child["child"] in sequence:
                    error_path = child["loc"]
                    error_msg = f"Dépendance circulaire"
                    user_msg = f"Une dépendance circulaire est causée par les composants : {sequence[-1]}, {child["child"]}"
                    focus_id = (sequence[-1], child["child"])
                    error_details_list.append(ErrorDetails(error_path, error_msg, focus_id))
                else:
                    new_seq = [*sequence, child["child"]]
                    sequences.update(_recursive(children_tree, new_seq, child["child"]))
            return sequence
          
        key = next(iter(children_tree))
        sequences.update(_recursive(children_tree, [key], key))
        
        for comp_id, comp_loc in zip(comps_id, comps_loc):
            if comp_id not in sequences:
                error_path = comp_loc
                error_msg = f"Tous les éléments doivent être connectés de près ou de loin au composant principal"
                focus_id = comp_id
                error_details_list.append(ErrorDetails(error_path, error_msg, focus_id))

        if error_details_list:
            error = LinksError(error_details_list)

        return error 
    
    @staticmethod
    def _algo_qt_structure(data:Dict[List[str]]) -> QtStructureError | None:
        """
        Vérifie que la hiérarchie des widgets Qt respecte les règles structurelles.

        Détecte les cas où un widget ou un composant custom est parent direct
        d'un autre widget, ce qui est interdit dans la hiérarchie Qt — un layout
        doit obligatoirement s'intercaler entre deux widgets.

        Args:
            data (Dict[List[str]]): Les identifiants et métadonnées extraits
                par `_extract_id`.

        Returns:
            QtStructureError | None: Une exception contenant les erreurs détectées,
                ou None si la hiérarchie est valide.
        """
        components_dict = data["components_dict"]
        children_tree = data["children_tree"]
        error_list = []
        error = None

        for comp_id, component in components_dict.items():
            category = component["category"]
            if category == "widget" or category == "custom":
                for child in children_tree[comp_id]:
                    child_id = child["child"]
                    if components_dict[child_id]["category"] == "widget":
                        error_path = component["loc"]
                        error_msg = f"widget {comp_id} ne peut pas être parent direct de {child_id}, car il est aussi un widget"
                        focus_id = (comp_id, child_id)
                        user_msg = f"Le widget {comp_id} ne peut pas être parent direct de {child_id}, car il est aussi un widget"
                        error_list.append(ErrorDetails(error_path, error_msg, focus_id))

        if error_list:
            error = QtStructureError(error_list)

        return error

    # variable statique, placée à la fin, car elle contient des fonctions de la classe
    _algo_list = ((_algo_unique_id, _algo_reference), (_algo_circular_dependency,), (_algo_qt_structure,))