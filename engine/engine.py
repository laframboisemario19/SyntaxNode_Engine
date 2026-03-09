from typing import Callable, List

from .strat.language_s import LanguageStrategy
from .strat.librairy_s import LibrairyStrategy

class SyntaxNodeEngine():
    def __init__(self):
        self.__lang_strategies = {}
        self.__current_lang_strategy = None
        self.__lib_strategies = {}
        self.__current_lib_strategy = None

        self._available_lang = []
        self._available_lib = []
        self._meta_objects = {}

    @property
    def available_lang(self) -> List[str]:
        return self._available_lang
    
    @property
    def available_lib(self) -> List[str]:
        return self._available_lib
    
    @property
    def current_lang(self) -> str:
        if self.__current_lang_strategy != None:
            return self.__current_lang_strategy.name
        else:
            return ""
    
    @property
    def current_lib(self) -> str:
        if self.__current_lib_strategy != None:  
            return self.__current_lib_strategy.name
        else:
            return ""
    
    def set_language(self, language:str):
            try:
                if language not in self.available_lang:  
                    raise Exception("erreur: langage sélectionné invalide")
            except Exception as e:
                print(e)
            else:
                self.__current_lang_strategy = self.__lang_strategies[language]
                self._available_lib = self.__current_lang_strategy.available_lib

    def set_lib(self, librairy:str):
                try:
                    if self.__current_lang_strategy == None:
                        raise Exception("erreur: il faut sélectionner un langage avant de définir la librairie.")
                    elif librairy not in self._available_lib:
                        raise Exception("erreur: librairie sélectionnée est invalide")
                except Exception as e:
                    print(e)
                else:
                    self.__current_lib_strategy = self.__lib_strategies[librairy]

    def add_lang_strategy(self, language:LanguageStrategy):
        try:
            if not isinstance(language, LanguageStrategy):
                raise Exception("erreur : paramètre invalide")
        except Exception as e:
            print(e)
        else:
            name = language.name
            self.__lang_strategies[name] = language
            self._available_lang.append(name)
    
    def add_lib_strategy(self, librairy:LibrairyStrategy):
        try:
            if not isinstance(librairy, LibrairyStrategy):
                raise Exception("erreur : paramètre invalide")
        except Exception as e:
            print(e)
        else:
            name = librairy.name
            self.__lib_strategies[name] = librairy
            self.__lang_strategies[librairy.language].add_lib(name)

    def get_meta_objects(self):
        try:
            if self.__current_lib_strategy == None:
                raise Exception("erreur : aucune librairie sélectionnée")
            else:
                return self.__current_lib_strategy.get_meta_objects()
        except Exception as e:
            print(e)
    