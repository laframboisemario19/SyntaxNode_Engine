from typing import Self, Any, List
import ast

class ASTFlattener():
    def __init__(self:Self) -> None:
        self.flatten_tree = []

    def flatten(self:Self, tree:ast.AST) -> List[List[Any]]:
        self.flatten_tree = []

        self._traverse(tree, None, "Module")
        return self.flatten_tree

    def _add_node(self:Self, type:str, parent_id:int | None, value:str | int | float | bool= "") -> int:
        node_id = len(self.flatten_tree)
        parent_id = parent_id if parent_id is not None else -1
        self.flatten_tree.append([type, parent_id, [], value])
        
        if parent_id != -1:
            self.flatten_tree[parent_id][2].append(node_id)

        return node_id

    def _traverse(self:Self, obj:ast.AST | List[Any], parent_id: int | None, obj_type: str) -> None:
        if isinstance(obj, ast.AST):
            node_type = f"AST_{obj.__class__.__name__}"
            current_id = self._add_node(node_type, parent_id)

            for fieldname, value in ast.iter_fields(obj):
                self._traverse(value, current_id, fieldname)
        
        elif isinstance(obj, list):
            if obj:
                list_id = self._add_node(f"AST_{obj_type}", parent_id)
                for item in obj:
                    self._traverse(item, list_id, obj_type)

        elif obj is not None or (obj is None and obj_type == "value"):
            self._add_node(f"AST_{obj_type}", parent_id, obj)