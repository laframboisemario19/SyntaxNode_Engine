from .ast_builder import ASTBuilder

class ASTDirector():
    def __init__(self, builder:ASTBuilder):
        self._builder = builder
    
    def change_builder(self, builder:ASTBuilder):
        self._builder = builder

    def make(self, data, metadata):
        self._builder.reset()
        self._builder.build_import()
