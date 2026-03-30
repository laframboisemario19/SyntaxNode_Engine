from abc import ABC, abstractmethod
from typing import Any

class LanguageStrategy(ABC):
    @abstractmethod
    def __init__(self, config=None):
        pass

    @abstractmethod
    def get_code_files(self, data:dict, metadata:dict):
        pass

class LibraryStrategy(ABC):
    @property
    @abstractmethod
    def metadata(self):
        pass

    @abstractmethod
    def __init__(self, config=None):
        pass

    @abstractmethod
    def get_meta_objects(self) -> dict[str, Any]:
        pass