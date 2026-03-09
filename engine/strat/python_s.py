from .language_s import LanguageStrategy

class PythonStrategy(LanguageStrategy):
    def __init__(self):
        self._name = "python"
        self._available_lib = []

    @property
    def name(self):
        return self._name
    
    @property
    def available_lib(self):
        return self._available_lib
    
    def add_lib(self, librairy:str):
        self._available_lib.append(librairy)

    def execute(self, request, data, metadata):
        pass