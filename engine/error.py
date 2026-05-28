"""
Exceptions personnalisées pour le moteur SyntaxNode.

Ce module définit la hiérarchie des erreurs spécifiques pouvant être levées 
lors de la configuration, de la résolution des stratégies ou de l'exécution 
du générateur d'AST et de code.
"""
from typing import Self, List, Tuple

class SyntaxNodeError(Exception):
    """Exception de base pour le moteur SyntaxNode."""
    pass

class UserException():
    """
    Marqueur indiquant que l'exception contient un message destiné à l'utilisateur.

    Les exceptions héritant de cette classe exposent un `user_msg` lisible par
    l'utilisateur final ainsi qu'un `msg` technique destiné au développeur.
    """
    pass

class DevException():
    """
    Marqueur indiquant que l'exception contient un message destiné exclusivement
    au développeur.

    Les exceptions héritant de cette classe exposent uniquement un `msg` technique
    et ne sont pas destinées à être affichées à l'utilisateur final.
    """
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
    """
    Conteneur structuré pour les détails d'une erreur individuelle.

    Attributes:
        loc (List[str]): Le chemin vers l'emplacement de l'erreur dans la structure JSON.
        msg (str): Le message technique destiné au développeur.
        focus_id (str | Tuple[str] | None): L'identifiant du ou des nœuds problématiques
            dans le graphe nodal, permettant de les surligner dans l'interface visuelle.
        user_msg (str): Le message destiné à l'utilisateur final.
    """
    def __init__(self:Self, loc:List[str], msg: str, focus_id:str|Tuple[str]|None = None, user_msg:str = "Une erreur inattendue est survenue. Veuillez contacter le soutien technique.") -> None:
        self.loc = loc
        self.msg = msg
        self.focus_id = focus_id
        self.user_msg = user_msg

class ErrorDetailsContainer(SyntaxNodeError):
    """
    Exception contenant une liste d'erreurs structurées de même type.

    Regroupe plusieurs `ErrorDetails` appartenant à une même catégorie d'erreur
    (ex: toutes les erreurs de références invalides).

    Attributes:
        error_detail_list (List[ErrorDetails]): La liste des erreurs individuelles.

    Examples:
        >>> except ErrorDetailsContainer as e:
        ...     for detail in e.error_detail_list:
        ...         print(f"Erreur : {detail.msg}")
        ...         print(f"Emplacement : {' -> '.join(detail.loc)}")
        ...         if detail.focus_id:
        ...             highlight_node(detail.focus_id)
    """
    def __init__(self:Self, error_detail_list:List[ErrorDetails]):
        """
        Initialise le conteneur avec une liste d'erreurs structurées.

        Args:
            error_detail_list (List[ErrorDetails]): La liste des erreurs individuelles
                appartenant à une même catégorie.
        """
        self.error_detail_list:List[ErrorDetails] = error_detail_list

    def __repr__(self:Self):
        message = ""
        for error_detail in self.error_detail_list:
            error_path = " -> ".join(error_detail.loc)
            error_msg = error_detail.msg
            message += f"{self.__class__.__name__} : Erreur à l'emplacement [{error_path}] : {error_msg}\n"
        return message
    
    def __str__(self:Self):
        message = ""
        for error_detail in self.error_detail_list:
            focus_id = error_detail.focus_id
            error_msg = error_detail.user_msg
            message += f"{self.__class__.__name__} : Erreur à l'emplacement [{focus_id}] : {error_msg}\n"
        return message
    
class ErrorContainer(SyntaxNodeError):
    """
    Exception regroupant plusieurs `ErrorDetailsContainer` de catégories différentes.

    Permet de remonter plusieurs groupes d'erreurs en une seule exception,
    évitant à l'appelant de découvrir les erreurs une catégorie à la fois.

    Attributes:
        error_list (List[ErrorDetailsContainer]): La liste des groupes d'erreurs.

    Examples:
        >>> except ErrorContainer as e:
        ...     for error_details_container in e.error_list:
        ...         for detail in error_details_container.error_detail_list:
        ...             print(f"Erreur : {detail.msg}")
        ...             print(f"Emplacement : {' -> '.join(detail.loc)}")
        ...             if detail.focus_id:
        ...                 highlight_node(detail.focus_id)
    """
    def __init__(self:Self, error_list:List[ErrorDetailsContainer]):
        """
        Initialise le conteneur avec une liste de groupes d'erreurs.

        Args:
            error_list (List[ErrorDetailsContainer]): La liste des groupes d'erreurs
                de catégories différentes.
        """
        self.error_list:List[ErrorDetailsContainer] = error_list
    
    def __repr__(self:Self):
        message = ""
        for error in self.error_list:
            message += repr(error)        
        return message
    
    def __str__(self:Self):
        message = ""
        for error in self.error_list:
            message += str(error)        
        return message

class JsonFormatError(ErrorDetailsContainer, DevException):
    """Levée quand la structure JSON des données ne respecte pas le schéma attendu."""
    pass

class UniqueIdError(ErrorDetailsContainer, DevException):
    """Levée quand des identifiants dupliqués sont détectés dans le projet."""
    pass

class ReferenceError(ErrorDetailsContainer, DevException):
    """Levée quand une référence pointe vers un identifiant inexistant dans le projet."""
    pass

class RootError(DevException):
    """Levée quand le projet ne respecte pas la structure de composants racine requise."""
    pass

class LinksError(ErrorDetailsContainer, UserException):
    """Levée quand des connexions invalides ou des dépendances circulaires sont détectées."""
    pass

class QtStructureError(ErrorDetailsContainer, UserException):
    """Levée quand la hiérarchie des widgets Qt ne respecte pas les règles structurelles."""
    pass

class CodeReferenceError(ErrorDetailsContainer, UserException):
    """Levée quand le code utilisateur référence une variable ou une fonction inconnue."""
    pass

class IllegalImportError(ErrorDetailsContainer, UserException):
    """Levée quand un module requis par un composant ne peut pas être importé."""
    pass

class FatalError(ErrorDetailsContainer, DevException, UserException):
    """Levée quand une fonction potentiellement malveillante est détectée dans le code utilisateur."""
    pass