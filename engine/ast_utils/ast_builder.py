from abc import ABC, abstractmethod
import ast

class ASTBuilder(ABC):

    @property
    @abstractmethod
    def tree(self):
        pass
    
    @abstractmethod
    def reset(self):
        pass
    
    @abstractmethod
    def create_tree(self):
        pass
    
    @abstractmethod
    def get_ast(self):
        pass

    @abstractmethod
    def build_import(self):
        pass

    @abstractmethod
    def build_node(self):
        pass

    def fix_locations(self):
        ast.fix_missing_locations(self._tree)