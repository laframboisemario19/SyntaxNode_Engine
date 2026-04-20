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
    def build_import(self, data):
        pass

    @abstractmethod
    def build_class(self, data):
        pass

    @abstractmethod
    def build_main(self, data_dict):
        pass

    @abstractmethod
    def _find_root(self, data):
        pass

    def print_tree(self):
        print(ast.dump(self._tree, indent=4))

    def fix_locations(self):
        ast.fix_missing_locations(self._tree)