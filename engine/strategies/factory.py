from enum import Enum

from .python_strategy import PythonStrategy
from .qt_strategy import QtStrategy
from ..config import TestConfig, DefaultConfig, ExtendedConfig
from .base import LanguageStrategy, LibraryStrategy

class StrategyType(Enum):
    LANGUAGE = 1
    LIBRARY = 2

class ConfigType(Enum):
    TEST = 1
    DEFAULT = 2
    EXTENDED = 3

class StrategyFactory:
    _strategies = {
        StrategyType.LANGUAGE : {
        "python": PythonStrategy
        },
        StrategyType.LIBRARY : {
        "qt": QtStrategy
        }
    }

    _configurations = {
        ConfigType.TEST : TestConfig,
        ConfigType.DEFAULT : DefaultConfig,
        ConfigType.EXTENDED : ExtendedConfig
    }
    
    @staticmethod
    def get_strategy(strategy_type: StrategyType, name: str, config: ConfigType = None) -> LibraryStrategy | LanguageStrategy:
        strategy = StrategyFactory._strategies.get(strategy_type).get(name)
        if not strategy:
            raise ValueError(f"{name} n'est pas implémentée.")
        if strategy_type == StrategyType.LIBRARY:
            if not config:
                raise ValueError(f"LibraryStrategy a besoin d'une ConfigType en argument.")
            if not StrategyFactory._configurations.get(config)():
                raise ValueError("Configuration non-reconnue")
            return strategy(config=StrategyFactory._configurations.get(config)())
        else:
            return strategy()
        
    @staticmethod
    def get_available(strategy_type: StrategyType) -> list[str]:
        return list(StrategyFactory._strategies.get(strategy_type).keys())
