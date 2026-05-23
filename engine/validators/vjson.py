from __future__ import annotations

from typing import List, Any, Optional, Literal, Dict, Set, Tuple
from ..error import *
from pydantic import BaseModel, ValidationError, field_validator

class InternFunction(BaseModel):
    id: str
    name: str
    is_intern: Literal[True]

class Function(BaseModel):
    id: str
    name: str
    params: List[str]
    code: List[str]
    is_intern: Literal[False]

class Properties(BaseModel):
    name: str
    type: Literal["int", "str", "float", "bool"]
    value: Optional[int | str | float | bool] = None

class EnumProperties(BaseModel):
    name: str
    type: Literal["enum"]
    namespace: List[str]
    value: str

class FlagProperties(BaseModel):
    name: str
    type: Literal["flag"]
    namespace: List[str]
    value: FlagValue

class ObjectProperties(BaseModel):
    name: str
    type: str
    module: str
    value: List[ObjectValue]

class Inheritance(BaseModel):
    type: str
    module: str

class FlagValue(BaseModel):
    exclusive: Dict[str, str]
    non_exclusive: List[str]

class ObjectValue(BaseModel):
    type: str
    value: str | List[Value] | int | bool | float
    name: str

class Value(BaseModel):
    type: str
    value: str | List[Value] | int | bool | float

class Variable(BaseModel):
    id: str
    name: str
    value: Value
    scope: Literal["public", "private"]

class Component(BaseModel):
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
    id: str
    source: str
    target: str
    type: str

class Project(BaseModel):
    id_project:str
    id_owner:str
    last_update:str
    project_name:str
    components: List[Component]
    links: List[Link]

class JsonValidator:

    @field_validator("components")
    @classmethod
    def validate_root_component(cls, components:List[Component]) -> List[Component]:
        if not components:
            raise RootError("Le projet doit avoir au minimum 1 composant.")
        if components[0].category != "custom":
            raise RootError("Le premier composant doit être de category custom.")
        
        for component in components[1:]:
            if component.category == "custom":
                raise RootError("Seul le premier composant peut être de category custom.")

        return components
    
    @staticmethod
    def validate_data(data: List[Dict[str, Any]]) -> bool:
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

    _algo_list = ((_algo_unique_id, _algo_reference), (_algo_circular_dependency,), (_algo_qt_structure,))