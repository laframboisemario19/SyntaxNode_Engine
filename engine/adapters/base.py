from abc import ABC, abstractmethod
from typing import Any

class MetadataAdapter(ABC):
    def __init__(self, cls:type):
        self._cls = cls

    @property
    def cls(self):
        return self._cls
    
    @property
    @abstractmethod
    def meta(self) -> Any:
        pass

    @property
    @abstractmethod
    def class_name(self) -> str:
        pass

    @property
    @abstractmethod
    def category(self) -> str:
        pass

    @property
    @abstractmethod
    def parent_class(self) -> str:
        pass

    @property
    @abstractmethod
    def module(self) -> str:
        pass

    @property
    @abstractmethod
    def is_abstract(self) -> bool:
        pass

    @property
    @abstractmethod
    def properties(self) -> dict[str, Any]:
        pass

    @property
    @abstractmethod
    def methods(self) -> dict[str, Any]:
        pass

    @abstractmethod
    def to_dict(self):
        pass

    @abstractmethod
    def _safe_instantiate(self):
        pass