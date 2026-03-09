from abc import ABC, abstractmethod

class LanguageStrategy(ABC):
    def execute(request, data, metadata):
        pass