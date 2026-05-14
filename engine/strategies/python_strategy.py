from typing import Self, Any, List, Dict, Tuple

from .base import LanguageStrategy, ImageGeneratorStrategy
from ..ast_utils import BuilderFactory, ASTDirector, ASTFlattener
from ..generator import CodeGenerator
from ..static_analyser import PyTorchModel
from ..visitors import ImportFromExtractor

class PythonStrategy(LanguageStrategy):
    def __init__(self, config=None):
        self._name = "python"
        self._image_generator: ImageGeneratorStrategy = None
        self._available_lib = []
        self._directors: dict[str, ASTDirector] = {}
        self._flattener = ASTFlattener()
        self._pytorch_model = None

    @property
    def name(self):
        return self._name
    
    @property
    def available_lib(self):
        return self._available_lib
        
    @property
    def image_generator(self: Self) -> str:
        return self._image_generator.name

    def get_code_files(self, library, data, metadata):
        if library not in self._directors:
            self._directors[library] = ASTDirector(BuilderFactory.get_builder(library))

        ast = self._directors[library].make(data, metadata)
        code = CodeGenerator.generate_code(ast)

        file = CodeGenerator.generate_file("main_application.py", code)
        zip_file = CodeGenerator.generate_zip_files((file,))

        return zip_file
    
    def generate_bitmap(self: Self, library:str, image_generator:ImageGeneratorStrategy, data: dict[Any, Any], metadata: dict[Any, Any], target_id:str):
        if image_generator.name != library:
            raise ValueError("image_generator n'est pas compatible avec la library spécifié.")
        
        if library not in self._directors:
            self._directors[library] = ASTDirector(BuilderFactory.get_builder(library))
            
        self._image_generator = image_generator
        
        tree = self._directors[library].make(data, metadata, target_id)

        return self._image_generator.generate_preview(tree)
    
    def train_ai(self:Self, library:str, data:Tuple[List[List[Any]]], metadata) -> None:
        if library not in self._directors:
            self._directors[library] = ASTDirector(BuilderFactory.get_builder(library))

        extractor = ImportFromExtractor()

        flat_ast_list = []
        for d in data:
            ast = self._directors[library].make(d, metadata)
            import_list = extractor.visit(ast)
            flat_ast = self._flattener.flatten(ast)
            flat_ast_list.append(flat_ast)
        
        if not self._pytorch_model:
            self._pytorch_model = PyTorchModel(tuple(flat_ast_list))
        else:
            self._pytorch_model.transform_data(tuple(flat_ast_list))