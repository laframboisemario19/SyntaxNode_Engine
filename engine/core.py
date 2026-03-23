from typing import Any

from .strategies import StrategyFactory, StrategyType, ConfigType

class SyntaxNodeEngine():
    def __init__(self):
        self.__current_lang_strategy = None
        self.__current_lib_strategy = None

    @property
    def available_lang(self) -> list[str]:
        return StrategyFactory.get_available(StrategyType.LANGUAGE)
    
    @property
    def available_lib(self) -> list[str]:
        return StrategyFactory.get_available(StrategyType.LIBRARY)
    
    @property
    def current_lang(self) -> str:
        if self.__current_lang_strategy:
            return self.__current_lang_strategy.name
        else:
            return ""
    
    @property
    def current_lib(self) -> str:
        if self.__current_lib_strategy:  
            return self.__current_lib_strategy.name
        else:
            return ""
    
    def set_language(self, language:str):
            self.__current_lang_strategy = StrategyFactory.get_strategy(StrategyType.LANGUAGE, language)

    def set_lib(self, library:str, config:ConfigType = ConfigType.TEST):
            if not self.__current_lang_strategy:
                raise RuntimeError("Erreur: Vous devez sélectionner un langage avant de définir la librairie.")
            else:
                self.__current_lib_strategy = StrategyFactory.get_strategy(StrategyType.LIBRARY, library, config)

    def get_meta_objects(self) -> dict[str, Any]:
        if not self.__current_lib_strategy:
            raise RuntimeError("Erreur : Aucune librairie n'a été sélectionnée")
        else:
            return self.__current_lib_strategy.get_meta_objects()
    
    def get_code_files(self, data):
        if not self.__current_lib_strategy:
            raise RuntimeError("Erreur : Aucune librairie n'a été sélectionnée")
        else:
            metadata = self.__current_lib_strategy.get_meta_objects()
            return self.__current_lang_strategy.get_code_files(self.current_lib, data, metadata)