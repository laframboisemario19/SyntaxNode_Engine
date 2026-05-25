"""
Interfaces de base pour le patron de conception Stratégie.

Ce module définit les contrats (Abstract Base Classes) que toutes les 
stratégies spécifiques (langages, bibliothèques, générateurs d'images) 
doivent respecter pour être utilisables par le SyntaxNodeEngine.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Self, Dict, List
from ast import Module
from io import BytesIO

from ..config import BaseConfig

class LanguageStrategy(ABC):
    """
    Contrat pour les stratégies de génération de code et d'orchestration de rendu.

    Toute nouvelle implémentation de langage (ex: C++, JavaScript) doit 
    hériter de cette classe et implémenter ces méthodes pour être compatible 
    avec le SyntaxNodeEngine.
    """
    @abstractmethod
    def __init__(self: Self, config: BaseConfig | None = None) -> None:
        """
        Initialise la stratégie avec une configuration optionnelle.

        Args:
            config (BaseConfig | None): Paramètres spécifiques au langage.
        """        
        pass

    @property
    @abstractmethod
    def name(self: Self) -> str:
        """
        Le nom identifiant le langage.

        Returns:
            str: Le nom en minuscules (ex: 'python', 'cpp').
        """
        pass

    @abstractmethod
    def get_code_files(self:Self, data:List[Dict[str, Any]], metadata:Dict[str, Any]):
        """
        Orchestre la création de l'AST et génère les fichiers sources compressés.

        Args:
            data (List[Dict[str, Any]]): Le graphe nodal configuré par l'utilisateur.
            metadata (Dict[str, Any]): Les métadonnées de la bibliothèque graphique.

        Returns:
            BytesIO: Un flux d'octets contenant l'archive (ex: .zip) des fichiers générés.
            
        Raises:
            SyntaxNodeError: Si la génération de l'AST échoue.
            ErrorDetailsContainer: Si les données contiennent des erreurs de validation structurelle.
            ErrorContainer: Si plusieurs groupes d'erreurs de validation sont détectés.
            FatalError: Si une fonction potentiellement malveillante est détectée dans le code utilisateur.
            IllegalImportError: Si un module requis par un composant ne peut pas être importé.
        """
        pass

    @abstractmethod
    def generate_bitmap(
        self: Self, 
        library: str, 
        image_generator: ImageGeneratorStrategy, 
        data: List[Dict[str, Any]], 
        metadata: Dict[str, Any],
        target_id: str
    ) -> BytesIO:
        """
        Orchestre la création de l'AST partiel et génère l'image d'aperçu d'un composant.

        Args:
            library (str): Le nom de la bibliothèque graphique cible.
            image_generator (ImageGeneratorStrategy): Le moteur de rendu à utiliser.
            data (List[Dict[str, Any]]): Le graphe nodal configuré par l'utilisateur.
            metadata (Dict[str, Any]): Les métadonnées de la bibliothèque graphique.
            target_id (str): L'identifiant unique du nœud à rendre.

        Returns:
            BytesIO: Le flux de données de l'image (ex: PNG) prête à l'affichage.

        Raises:
            SyntaxNodeError: Si la génération de l'AST échoue.
            ErrorDetailsContainer: Si les données contiennent des erreurs de validation structurelle.
            ErrorContainer: Si plusieurs groupes d'erreurs de validation sont détectés.
            FatalError: Si une fonction potentiellement malveillante est détectée dans le code utilisateur.
            IllegalImportError: Si un module requis par un composant ne peut pas être importé.
        """
        pass

    @abstractmethod
    def validate_ast(self:Self, library:str, data:List[Dict[str, Any]], metadata: Dict[str, Any]) -> bool:
        """
        Valide la cohérence de l'AST généré à partir des données du graphe nodal.

        Args:
            library (str): Le nom de la bibliothèque graphique cible.
            data (List[Dict[str, Any]]): Le graphe nodal configuré par l'utilisateur.
            metadata (Dict[str, Any]): Les métadonnées de la bibliothèque graphique.

        Returns:
            bool: True si l'AST généré est valide, False sinon.

        Raises:
            SyntaxNodeError: Si la génération de l'AST échoue.
            ErrorDetailsContainer: Si les données contiennent des erreurs de validation structurelle.
            ErrorContainer: Si plusieurs groupes d'erreurs de validation sont détectés.
            FatalError: Si une fonction potentiellement malveillante est détectée dans le code utilisateur.
            IllegalImportError: Si un module requis par un composant ne peut pas être importé.
        """
        pass
    
    @abstractmethod
    def train_ai(self:Self, library:str, metadata) -> None:
        """
        Déclenche l'entraînement du modèle d'analyse statique.

        L'acquisition des données d'entraînement est gérée à l'interne par une
        factory dédiée.

        Args:
            library (str): Le nom de la bibliothèque graphique cible.
            metadata: Les métadonnées de la bibliothèque graphique.
        """
        pass

    @abstractmethod
    def predict(self:Self, library:str, data: List[Dict[str, Any]], metadata: Dict[str, Any]):
        """
        Effectue une prédiction sur le code utilisateur via le modèle d'analyse statique.

        Args:
            library (str): Le nom de la bibliothèque graphique cible.
            data (List[Dict[str, Any]]): Le graphe nodal configuré par l'utilisateur.
            metadata (Dict[str, Any]): Les métadonnées de la bibliothèque graphique.

        Returns:
            float: Un score indiquant si le code est considéré sûr ou non,
                à comparer avec les seuils de `PredictionValue`.
        """
        pass

class LibraryStrategy(ABC):
    """
    Contrat pour les stratégies gérant les métadonnées des bibliothèques graphiques.

    Toute nouvelle implémentation de bibliothèque (ex: Tkinter, Kivy) doit 
    hériter de cette classe pour exposer ses composants et sa logique au moteur.
    """
    @abstractmethod
    def __init__(self:Self, config:BaseConfig | None = None):
        """
        Initialise la stratégie de la bibliothèque avec une configuration.

        Args:
            config (BaseConfig | None): Paramètres de démarrage spécifiques 
                à la bibliothèque.
        """
        pass

    @property
    @abstractmethod
    def name(self: Self) -> str:
        """
        Le nom identifiant la bibliothèque graphique.

        Returns:
            str: Le nom en minuscules (ex: 'qt', 'tkinter').
        """
        pass

    @property
    @abstractmethod
    def metadata(self:Self) -> Dict[str, Any]:
        """
        Dictionnaire contenant les données de configuration globales de la bibliothèque.

        Returns:
            Dict[str, Any]: Les métadonnées (ex: version, dépendances requises, 
            règles spécifiques de rendu).
        """
        pass

    @abstractmethod
    def get_meta_objects(self:Self) -> Dict[str, Any]:
        """
        Retourne les objets structurels disponibles pour l'interface visuelle.

        Returns:
            Dict[str, Any]: Un dictionnaire cataloguant les classes, widgets 
            et propriétés disponibles pour la construction du graphe nodal.
            
        Raises:
            SyntaxNodeError: Si l'introspection de la bibliothèque échoue ou 
                si les données sont corrompues.
        """
        pass

class ImageGeneratorStrategy(ABC):
    """
    Contrat pour les moteurs de rendu visuel (offscreen rendering).
    
    Définit comment un arbre syntaxique partiel est compilé et converti en 
    une image bitmap pour l'aperçu dans l'interface nodale.
    """
    @property
    @abstractmethod
    def name(self: Self) -> str:
        """
        Le nom identifiant le générateur d'image.

        Returns:
            str: Le nom de la bibliothèque à laquelle le générateur correspond (ex: 'qt').
        """
        pass

    @property
    @abstractmethod
    def output_format(self: Self) -> str:
        """
        Le format d'exportation de l'image.

        La modification de cette propriété (via son setter) ajustera le format 
        qui sera utilisé lors du prochain appel à `generate_preview`.

        Returns:
            str: Le format d'image actuel (ex: 'PNG', 'JPEG').
        """
        pass

    @output_format.setter
    @abstractmethod
    def output_format(self: Self, output_format: str) -> None:
        pass

    @abstractmethod
    def generate_preview(self: Self, ast_root: Module) -> BytesIO:
        """
        Compile un arbre syntaxique et retourne l'image générée en mémoire.

        Args:
            ast_root (Module): Le nœud racine (ast.Module) contenant 
                la logique d'interface à rendre de manière isolée.

        Returns:
            BytesIO: Un flux d'octets contenant l'image graphique prête 
            à être expédiée au client.
            
        Raises:
            SyntaxNodeError: Si le rendu de l'image échoue, si l'AST est invalide 
                ou si la mémoire est insuffisante.
        """
        pass