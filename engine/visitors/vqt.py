import ast
from typing import Self, List, override

class ImportFromExtractor(ast.NodeVisitor):
    def __init__(self:Self):
        self._import_list = []

    @override
    def generic_visit(self:Self, node:ast.AST):
        self._import_list = []
        super().generic_visit(node)
        return self._import_list
    
    @override
    def visit_ImportFrom(self:Self, node:ast.ImportFrom):
        for alias in node.names:
            name = alias.name
            if name not in ("true_property", "snake_case"):
                self._import_list.append(alias.name)
        self.generic_visit(node)
    

