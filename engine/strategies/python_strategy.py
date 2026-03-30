from .base import LanguageStrategy
from ..ast_utils import BuilderFactory, ASTDirector

class PythonStrategy(LanguageStrategy):
    def __init__(self, config=None):
        self._name = "python"
        self._available_lib = []
        self._directors = {}

    @property
    def name(self):
        return self._name
    
    @property
    def available_lib(self):
        return self._available_lib

    def get_code_files(self, library, data, metadata):
        if library not in self._directors:
            self._directors[library] = ASTDirector(BuilderFactory.get_builder(library))
        return self._directors[library].make(data, metadata)