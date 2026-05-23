import ast
import importlib
import builtins
from typing import List, Dict, Any, Self, override
from ..error import CodeReferenceError, ErrorContainer, IllegalImportError, ErrorDetails, FatalError

from __feature__ import true_property, snake_case #type: ignore[import-not-found]

class FunctionValidator(ast.NodeVisitor):
    _BUILTIN_FUNCTIONS = set(func_name for func_name, func in builtins.__dict__.items() if callable(func))
    _BLACK_LIST = set(["eval", "exec", "compile", "open", "__import__", "__builtins__", "__globals__", "__class__", "__subclasses__", "sys"])
    

    def __init__(self:Self):
        self._error_details_list = []
        self._error_type = CodeReferenceError
        self._valid_variable = set()
        self._valid_function = set()
        self._local_variable = set()
        self._is_init_function = True
        self._class_node = None

        self._target_attribute_visitor = _TargetAttributeVisitor()
  
    @override
    def visit_ClassDef(self, node):
        self._valid_variable = getattr(node, "sn_local_variable", []).copy()
        self._valid_function = getattr(node, "sn_local_function", []).copy()
        self._class_node = node
        self.generic_visit(node)

    @override
    def visit_FunctionDef(self: Self, node:ast.FunctionDef):
        self._local_variable = set()
        self._is_init_function = node.name == "__init__"
        param_names = {param.arg for param in node.args.args}
        self._local_variable.update(param_names)

        if node.name != "main":
            self.generic_visit(node)

    @override
    def visit_Assign(self:Self, node:ast.Assign):
        for target in node.targets:
            self._target_attribute_visitor._attribute = ""
            self._target_attribute_visitor._is_local = True
            self._target_attribute_visitor.visit(target)
            if self._target_attribute_visitor._is_local:
                self._local_variable.add(self._target_attribute_visitor._attribute)
            elif self._is_init_function:
                self._valid_variable.add(self._target_attribute_visitor._attribute)
            elif self._target_attribute_visitor._attribute not in (self._valid_variable | self._local_variable):
                sn_loc = getattr(self._class_node, "sn_loc", [])
                sn_id = getattr(self._class_node, "sn_id", "")
                msg = f"Création de variable de classe interdite dans les fonctions. Variable : {self._target_attribute_visitor._attribute} invalide"
                user_msg = f"Création de variable de classe interdite dans les fonctions."
                error_detail = ErrorDetails(sn_loc, msg, sn_id, user_msg)
                self._error_details_list.append(error_detail)

        self.visit(node.value)

    @override
    def visit_Name(self:Self, node:ast.Name) -> None:
        if self._is_init_function or node.id == "self":
            return
        elif node.id in FunctionValidator._BLACK_LIST:
            sn_loc = getattr(self._class_node, "sn_loc", [])
            sn_id = getattr(self._class_node, "sn_id", "")
            msg = f"Fonction potentiellement malveillante, requête refusée"
            user_msg = f"Une erreur est survenue. Impossible de traiter la requête."
            error_detail = ErrorDetails(sn_loc, msg, sn_id, user_msg)
            raise FatalError(error_detail)
        elif node.id not in (self._local_variable | self._valid_variable):
            msg = f"variable {node.id} inconnue"
            error_detail = ErrorDetails(self._class_node.sn_loc, msg, self._class_node.sn_id, msg)
            self._error_details_list.append(error_detail)

    @override
    def visit_Call(self:Self, node:ast.Call) -> None:
        if self._is_init_function:
            return
        self._target_attribute_visitor.visit(node.func)
        func_name = self._target_attribute_visitor._attribute
        if func_name not in (self._valid_function | self._BUILTIN_FUNCTIONS | self._local_variable | self._valid_variable):
            sn_loc = getattr(self._class_node, "sn_loc", [])
            sn_id = getattr(self._class_node, "sn_loc", "")
            msg = f"L'identifiant {func_name} inconnue"
            error_detail = ErrorDetails(sn_loc, msg, sn_id, msg)
            self._error_details_list.append(error_detail)
        for func_arg in node.args:
            self.generic_visit(func_arg)

    @override
    def visit_If(self:Self, node:ast.Compare) -> None:
        node_id = getattr(node, "sn_id", "")
        if node_id and node_id == "__main__":
            return
        else:
            self.generic_visit(node)
        
class _TargetAttributeVisitor(ast.NodeVisitor):
    def __init__(self:Self) -> None:
        self._attribute = ""
        self._is_local = True
        

    @override
    def visit_Attribute(self:Self, node:ast.Attribute):
        self.generic_visit(node)
        if self._attribute == "self":
            self._attribute += f".{node.attr}"

    @override
    def visit_Name(self:Self, node:ast.Name):
        self._attribute = node.id
        self._is_local = node.id != "self"
        

class ASTValidator:
    def __init__(self:Self):
        self._loc_dict = {}
        self._local_variable = {}
        self._local_function = {}
        self._validators = (FunctionValidator(),)
    
    def insert_details(self:Self, node:ast.AST, node_id:str):
        node.sn_id = node_id

        if node_id == "__main__":
            return
        
        node.sn_loc = self._loc_dict[node_id]
        node.sn_local_variable = self._local_variable[node_id]
        node.sn_local_function = self._local_function[node_id]

    def config(self:Self, data: List[Dict[str, Any]]):
        self._loc_dict = {}
        self._extract_details(data)

    def validate_data(self:Self, tree: ast.AST):
        error_list = []
        for validator in self._validators:
            validator.visit(tree)

            if validator._error_details_list:
                error_list.append(validator._error_type(validator._error_details_list))

        if error_list:
            raise ErrorContainer(error_list)

    def _extract_details(self:Self, data: Dict[str, Any]):
        for i, component in enumerate(data.get("components", [])):
            loc = ["components", str(i), "id"]
            self._loc_dict[component["id"]] = loc
            self._local_variable[component["id"]] = set()
            self._local_function[component["id"]] = set()

            inheritance = component["inheritance"]
            if inheritance:
                inheritance = inheritance[0]
                module_name = inheritance["module"]
                class_name = inheritance["type"]
            else:
                module_name = component["module"]
                class_name = component["type"]

            try:
                obj_module = importlib.import_module(module_name)
                obj_class = getattr(obj_module, class_name)
                inherited_attr = dir(obj_class)
                for attr in inherited_attr:
                    if callable(getattr(obj_class, attr)) and not attr.startswith("__"):
                        self._local_function[component["id"]].add(f"self.{attr}")
                    else:
                        self._local_variable[component["id"]].add(f"self.{attr}")
            except Exception as e:
                error_detail = ErrorDetails(loc, f"Impossible d'importer {class_name} du module {module_name}", component["id"], f"Il n'est pas possible de faire des imports à l'intérieur des fonctions.")
                raise IllegalImportError([error_detail])

            for variable in component.get("variable", []):
                self._local_variable[component["id"]].add(f"self.{variable.get('name')}")

            for function in component.get("function", []):
                self._local_function[component["id"]].add(f"self.{function.get('name')}")
