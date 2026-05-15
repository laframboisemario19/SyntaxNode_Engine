"""
Exceptions personnalisées pour le moteur SyntaxNode.

Ce module définit la hiérarchie des erreurs spécifiques pouvant être levées 
lors de la configuration, de la résolution des stratégies ou de l'exécution 
du générateur d'AST et de code.
"""
from typing import Self, List, Tuple

__all__ = ["SyntaxNodeError", "EngineNotConfiguredError", "StrategyNotFoundError", "TypeJsonFormatError", "ErrorDetails",
           "ErrorDetailsContainer", "ErrorContainer", "JsonFormatError", "UniqueIdError", "ReferenceError",
           "CircularDependencyError", "QtComplianceError"]

class SyntaxNodeError(Exception):
    """Exception de base pour le moteur SyntaxNode."""
    pass

class UserException():
    pass

class DevException():
    pass

class EngineNotConfiguredError(SyntaxNodeError):
    """Levée quand on tente d'exécuter une action sans la bonne configuration."""
    pass

class StrategyNotFoundError(SyntaxNodeError):
    """Levée quand la librairie ou le langage demandé n'existe pas."""
    pass

class TypeJsonFormatError(SyntaxNodeError):
    pass

class ErrorDetails():
    def __init__(self:Self, loc:List[str], msg: str, focus_id:str|Tuple[str]|None = None):
        self.loc = loc
        self.msg = msg
        self.focus_id = focus_id

class ErrorDetailsContainer(SyntaxNodeError):
    def __init__(self:Self, error_detail_list:List[ErrorDetails]):
        self.error_detail_list:List[ErrorDetails] = error_detail_list

    def __str__(self:Self):
        message = ""
        for error_detail in self.error_detail_list:
            error_path = " -> ".join(error_detail.loc)
            error_msg = error_detail.msg
            message += f"{self.__class__.__name__} : Erreur à l'emplacement [{error_path}] : {error_msg}\n"
        return message
    
class ErrorContainer(SyntaxNodeError):
    def __init__(self:Self, error_list:List[ErrorDetailsContainer]):
        self.error_list:List[ErrorDetailsContainer] = error_list
    
    def __str__(self:Self):
        message = ""
        for error in self.error_list:
            message += str(error)        
        return message

class JsonFormatError(ErrorDetailsContainer, DevException):
    pass

class UniqueIdError(ErrorDetailsContainer, DevException):
    pass

class ReferenceError(ErrorDetailsContainer, DevException):
    pass

class CircularDependencyError(ErrorDetailsContainer, UserException):
    pass

class TooManyRootError(ErrorDetailsContainer, UserException):
    pass

class QtComplianceError(ErrorDetailsContainer,UserException):
    pass