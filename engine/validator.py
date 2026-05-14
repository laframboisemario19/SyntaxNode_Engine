from __future__ import annotations

from typing import List, Any, Optional, Literal
from .error import JsonFormatError
from pydantic import BaseModel, ValidationError

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
    type: str
    module: str
    value: List[Value]

class Inheritance(BaseModel):
    type: str
    module: str

class Value(BaseModel):
    type: str
    value: str | List[Value] | int | bool | float
    name: Optional[str] = None

class Variable(BaseModel):
    id: str
    name: str
    value: Value

class Component(BaseModel):
    id: str
    type: str
    category: str
    name: str
    module: str
    child: List[str]
    variable: List[Variable]
    inheritance: List[Inheritance]
    function: List[Function | InternFunction]

class Link(BaseModel):
    id: str
    source: str
    target: str
    type: str
    type: str

class Project(BaseModel):
    components: List[Component]
    links: List[Link]

class SyntaxNodeValidator:
    @staticmethod
    def validate_data(data: Any) -> bool:
        if not isinstance(data, list):
            raise JsonFormatError(f"Les données doivent être de type list et non de type {data.__class__.__name__}")
        
        for project_data in data:
            if not isinstance(project_data, dict):
                raise JsonFormatError(f"Les projets doivent être de type dict et non de type {project_data.__class__.__name__}")
            
            try:
                Project(**project_data) 
            except ValidationError as e:
                error_detail = e.errors()[0]
                
                error_path = " -> ".join([str(loc) for loc in error_detail["loc"]])
                error_msg = error_detail["msg"]
                
                raise JsonFormatError(f"Erreur de validation à l'emplacement [{error_path}] : {error_msg}")

        return True