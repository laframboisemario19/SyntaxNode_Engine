"""
Paquet principal du moteur SyntaxNode.

Ce paquet expose l'interface publique permettant d'instancier le générateur 
d'AST et de gérer les stratégies de compilation visuelle (Python/Qt). 

Il centralise également les exceptions personnalisées du moteur pour 
faciliter la gestion des erreurs côté serveur.

Composants publics :
    - SyntaxNodeEngine : La classe principale d'orchestration.
    - SyntaxNodeError : L'exception de base.
    - EngineNotConfiguredError : Erreur de configuration.
    - StrategyNotFoundError : Erreur de sélection de stratégie.
"""

from .core import SyntaxNodeEngine
from .error import (SyntaxNodeError, EngineNotConfiguredError, StrategyNotFoundError, TypeJsonFormatError, ErrorDetails, ErrorDetailsContainer,
ErrorContainer, JsonFormatError, UniqueIdError, ReferenceError, QtStructureError, RootError, LinksError, CodeReferenceError, FatalError)

__all__ = ["SyntaxNodeEngine", "SyntaxNodeError", "EngineNotConfiguredError", "StrategyNotFoundError", "TypeJsonFormatError", "ErrorDetails",
           "ErrorDetailsContainer", "ErrorContainer", "JsonFormatError", "UniqueIdError", "ReferenceError", "QtStructureError", "RootError", "LinksError",
           "CodeReferenceError", "FatalError"]