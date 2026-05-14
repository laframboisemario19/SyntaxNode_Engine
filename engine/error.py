"""
Exceptions personnalisées pour le moteur SyntaxNode.

Ce module définit la hiérarchie des erreurs spécifiques pouvant être levées 
lors de la configuration, de la résolution des stratégies ou de l'exécution 
du générateur d'AST et de code.
"""

class SyntaxNodeError(Exception):
    """Exception de base pour le moteur SyntaxNode."""
    pass

class EngineNotConfiguredError(SyntaxNodeError):
    """Levée quand on tente d'exécuter une action sans la bonne configuration."""
    pass

class StrategyNotFoundError(SyntaxNodeError):
    """Levée quand la librairie ou le langage demandé n'existe pas."""
    pass

class JsonFormatError(SyntaxNodeError):
    pass