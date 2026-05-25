"""
Paquet principal du moteur SyntaxNode.

Ce paquet expose l'interface publique permettant d'instancier le générateur
d'AST et de gérer les stratégies de compilation visuelle (Python/Qt).

Il centralise également les exceptions personnalisées du moteur pour
faciliter la gestion des erreurs côté serveur.

Classes
-------
SyntaxNodeEngine: Classe principale d'orchestration du moteur.
PredictionValue: Énumération des seuils de décision pour l'analyse statique.
SyntaxNodeError: Exception de base du moteur.
UserException: Marqueur pour les exceptions contenant un message utilisateur.
DevException: Marqueur pour les exceptions contenant un message développeur.
EngineNotConfiguredError: Levée lors d'une action sans la bonne configuration.
StrategyNotFoundError: Levée quand le langage ou la bibliothèque demandé n'existe pas.
TypeJsonFormatError: Levée quand le type des données passées est invalide.
ErrorDetails: Conteneur structuré pour les détails d'une erreur individuelle.
ErrorDetailsContainer: Exception regroupant des erreurs de même catégorie.
ErrorContainer: Exception regroupant plusieurs groupes d'erreurs.
JsonFormatError: Levée quand la structure JSON ne respecte pas le schéma attendu.
UniqueIdError: Levée quand des identifiants dupliqués sont détectés.
ReferenceError: Levée quand une référence pointe vers un identifiant inexistant.
RootError: Levée quand la structure de composants racine n'est pas respectée.
LinksError: Levée quand des connexions invalides ou circulaires sont détectées.
QtStructureError: Levée quand la hiérarchie des widgets Qt est invalide.
CodeReferenceError: Levée quand le code référence une variable ou fonction inconnue.
IllegalImportError: Levée quand un module requis ne peut pas être importé.
FatalError: Levée quand une fonction potentiellement malveillante est détectée.
"""
from .core import SyntaxNodeEngine, PredictionValue
from .error import (SyntaxNodeError, EngineNotConfiguredError, StrategyNotFoundError, TypeJsonFormatError, ErrorDetails, ErrorDetailsContainer,
ErrorContainer, JsonFormatError, UniqueIdError, ReferenceError, QtStructureError, RootError, LinksError, CodeReferenceError, FatalError, IllegalImportError,
UserException, DevException)

__all__ = ["SyntaxNodeEngine", "PredictionValue", "SyntaxNodeError", "EngineNotConfiguredError", "StrategyNotFoundError", "TypeJsonFormatError", "ErrorDetails",
           "ErrorDetailsContainer", "ErrorContainer", "JsonFormatError", "UniqueIdError", "ReferenceError", "QtStructureError", "RootError", "LinksError",
           "CodeReferenceError", "FatalError", "IllegalImportError", "UserException", "DevException"]