from abc import ABC, abstractmethod
from typing import Any

class LanguageStrategy(ABC):
    @abstractmethod
    def __init__(self, config=None):
        pass

    # @abstractmethod
    # def add_lib(self, librairy:str):
    #     pass

    @abstractmethod
    def get_code_files(self, data:dict, metadata:dict):
        pass

class LibraryStrategy(ABC):
    @abstractmethod
    def __init__(self, config=None):
        pass

    @abstractmethod
    def get_meta_objects(self) -> dict[str, Any]:
        pass