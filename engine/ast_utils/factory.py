from .qt_ast_builder import QtASTBuilder
from .ast_builder import ASTBuilder

class BuilderFactory:
    _builders = {"qt":QtASTBuilder}
    
    @classmethod
    def get_builder(cls, library: str) -> ASTBuilder:
        return cls._builders[library]()
