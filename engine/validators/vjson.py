from __future__ import annotations

from typing import List, Any, Optional, Literal, Dict, Set, Tuple
from ..error import JsonFormatError, TypeJsonFormatError, ErrorDetails
from pydantic import BaseModel, ValidationError
from collections import Counter

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
        
        # JsonValidator._validate_data_structure(project_data)


        return True
    
    @staticmethod
    def _validate_data_structure(data: Dict[str, Any]) -> bool:
        error_list = []

        components_id, components_loc, \
            variable_id, variable_loc, \
            function_id, function_loc, \
            link_id, link_loc, \
            children_tree = JsonValidator._extract_id(data)

        return True
    
    @staticmethod
    def _extract_id(data: Dict[str, Any]) -> Tuple[List[str]]:
        components_id = []
        components_loc = []

        variable_id = []
        variable_loc = []

        function_id = []
        function_loc = []

        link_id = []
        link_loc = []

        children_tree = {}

        for i, component in enumerate(data.get("components", [])):
            components_id.append(component["id"])
            components_loc.append(["components", str(i), "id"])

            for j, variable in enumerate(component.get("variable", [])):
                variable_id.append(variable["id"])
                variable_loc.append(["components", str(i), "variable", str(j), "id"])

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

        return (components_id, components_loc, variable_id, variable_loc, function_id, function_loc, link_id, link_loc, children_tree)