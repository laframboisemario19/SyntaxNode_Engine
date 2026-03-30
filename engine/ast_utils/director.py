from .ast_builder import ASTBuilder
from ..utils import MetadataSerializer as mds

class ASTDirector():
    def __init__(self, builder:ASTBuilder):
        self._builder = builder
    
    def change_builder(self, builder:ASTBuilder):
        self._builder = builder

    def make(self, data, metadata):
        data = data[0]
        mds.sanitize_properties(data["components"], metadata)

        self._builder.reset()
        self._builder.create_tree()        
        self._builder.build_import(data["components"])

        data_dict = mds.list_to_map(data["components"])

        self._builder.build_class(data, data_dict)
        self._builder.build_main(data_dict)
        self._builder.fix_locations()
        self._builder.print_tree()
        return self._builder.get_ast()
