"""
Usine de stratégies pour le moteur SyntaxNode.

Ce module implémente le patron de conception Fabrique (Factory) combiné 
aux Stratégies. Il est responsable d'instancier la bonne logique selon 
les choix de l'utilisateur (langage, bibliothèque graphique).
"""

from enum import Enum

from .python_strategy import PythonStrategy
from .qt_strategy import QtStrategy, QtOffScreenGenerator
from ..config import TestConfig, DefaultConfig, ExtendedConfig
from .base import LanguageStrategy, LibraryStrategy, ImageGeneratorStrategy

from ..error import SyntaxNodeError, StrategyNotFoundError

class StrategyType(Enum):
    """Énumération des types de stratégies disponibles dans l'usine."""
    LANGUAGE = 1
    LIBRARY = 2
    IMG_GENERATOR = 3

class ConfigType(Enum):
    """Énumération des niveaux de configuration pour les bibliothèques."""
    TEST = 1
    DEFAULT = 2
    EXTENDED = 3

class StrategyFactory:
    """
    Classe utilitaire statique agissant comme usine de stratégies.
    """
    _strategies = {
        StrategyType.LANGUAGE : {
            "python": PythonStrategy
        },
        StrategyType.LIBRARY : {
            "qt": QtStrategy
        },
        StrategyType.IMG_GENERATOR : {
            "qt": QtOffScreenGenerator
        }

    }

    _configurations = {
        ConfigType.TEST : TestConfig,
        ConfigType.DEFAULT : DefaultConfig,
        ConfigType.EXTENDED : ExtendedConfig
    }
    
    @staticmethod
    def get_strategy(strategy_type: StrategyType, name: str, config: ConfigType | None = None) -> LibraryStrategy | LanguageStrategy | ImageGeneratorStrategy:
        """
        Instancie et retourne la stratégie demandée.

        Args:
            strategy_type (StrategyType): La catégorie de la stratégie.
            name (str): Le nom de la stratégie (insensible à la casse).
            config (ConfigType | None, optional): La configuration requise pour 
                les stratégies de type LIBRARY.

        Returns:
            LibraryStrategy | LanguageStrategy | ImageGeneratorStrategy: Une instance 
            prête à l'emploi de la stratégie demandée.

        Raises:
            TypeError: Si strategy_type n'est pas un Enum StrategyType valide.
            StrategyNotFoundError: Si le nom de la stratégie n'existe pas.
            SyntaxNodeError: Si une bibliothèque est instanciée sans configuration, 
                ou avec une configuration invalide.

        Examples:
            >>> # Instanciation d'une stratégie de langage
            >>> strat = StrategyFactory.get_strategy(StrategyType.LANGUAGE, "python")
            >>> strat.name
            'python'
            
            >>> # Démonstration de la normalisation (insensible à la casse)
            >>> strat_maj = StrategyFactory.get_strategy(StrategyType.LANGUAGE, "  PyThOn  ")
            >>> strat_maj.name
            'python'
        """

        if not isinstance(strategy_type, StrategyType):
            raise TypeError(f"L'argument strategy_type doit être un StrategyType, reçu: {type(strategy_type)}")
        
        name_normalized = str(name).lower().strip()

        strategy_dict = StrategyFactory._strategies.get(strategy_type)
        strategy_class = strategy_dict.get(name_normalized)

        if not strategy_class:
            raise StrategyNotFoundError(
                f"La stratégie '{name_normalized}' n'est pas implémentée pour {strategy_type.name}."
            )
        
        if strategy_type == StrategyType.LIBRARY:
            if config is None:
                raise SyntaxNodeError(f"L'instanciation de {name_normalized} nécessite un ConfigType en argument.")
            
            if config not in StrategyFactory._configurations:
                raise SyntaxNodeError(f"Configuration non reconnue : {config}")
            
            config_instance = StrategyFactory._configurations[config]()
            return strategy_class(config=config_instance)
            
        else:
            return strategy_class()
        
    @staticmethod
    def get_available(strategy_type: StrategyType) -> list[str]:
        """
        Retourne la liste des stratégies implémentées pour un type donné.

        Args:
            strategy_type (StrategyType): La catégorie à inspecter.

        Returns:
            list[str]: Une liste des noms disponibles (ex: ['python']).
            
        Raises:
            TypeError: Si strategy_type n'est pas un Enum StrategyType valide.

        Examples:
            >>> StrategyFactory.get_available(StrategyType.LANGUAGE)
            ['python']
            >>> StrategyFactory.get_available(StrategyType.LIBRARY)
            ['qt']
        """
        if not isinstance(strategy_type, StrategyType):
            raise TypeError("L'argument strategy_type doit être un StrategyType.")
        
        return list(StrategyFactory._strategies.get(strategy_type, {}).keys())
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()
    print("Tests documentaires de l'usine terminés.")
