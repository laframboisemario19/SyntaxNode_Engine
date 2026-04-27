from typing import Self, Any
import ast
from ast import NodeVisitor

class ASTFlattener():
    def __init__(self:Self):
        pass

    def flatten(self:Self, ast:ast.Module):
        visitor = FlattenerVisitor()
        visitor.visit(ast)
        flatten_tree = visitor.flatten_tree
        pass


class FlattenerVisitor(NodeVisitor):
    def __init__(self:Self):
        super().__init__()
        self._count = 0
        self.flatten_tree = []
        self._current_parent_id = None

    def generic_visit(self:Self, node:Any):
        super().generic_visit(node)

    def visit_Module(self:Self, node:Any):
        self.flatten_tree.append(["AST.Module", None, [], ""])
        for n in node.body:
            self._current_parent_id = 0
            self.visit(n)

    def visit_Import(self:Self, node:Any):
        self._add_node("AST.Import", has_child=True)
        self._add_node("AST.names", has_child=True)
        for name in node.names:
            self._add_node("AST.alias", name.name, has_child=False)

    def visit_ImportFrom(self:Self, node:Any):
        self._add_node("AST.Import", has_child=True)
        self._add_node("AST.module", node.module, has_child=False)
        self._add_node("AST.names", has_child=True)
        for name in node.names:
            self._add_node("AST.alias", name.name, has_child=False)

    def visit_ClassDef(self:Self, node:Any):
        self_id = len(self.flatten_tree)
        self._add_node("AST.ClassDef", value=node.name, has_child=True)
        self._add_node("AST.base", has_child=True)
        for b in node.bases:
            self.visit(b)

    def visit_Name(self:Self, node:Any):
        self._add_node("AST.Name", node.id, has_child=False)

    def _add_node(self:Self, type:str, value:str= "", has_child:bool=False):
        self.flatten_tree.append([type, self._current_parent_id, [], value])
        self.flatten_tree[self._current_parent_id][2].append(len(self.flatten_tree) - 1)
        if has_child:
            self._current_parent_id = len(self.flatten_tree) - 1