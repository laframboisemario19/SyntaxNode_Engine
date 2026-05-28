"""
Implémentation des stratégies Qt pour le moteur SyntaxNode.

Ce module fournit la classe `QtStrategy`, qui gère les métadonnées des
composants Qt disponibles pour la construction du graphe nodal, ainsi que
`QtOffScreenGenerator`, qui orchestre le rendu visuel offscreen des
composants via PySide6.

Classes
-------
QtStrategy: Stratégie concrète de gestion des métadonnées pour la bibliothèque Qt.
QtOffScreenGenerator: Moteur de rendu visuel offscreen pour les aperçus Qt.
"""

import sys

import PySide6
from __feature__ import snake_case, true_property # type: ignore[import-not-found]

from PySide6.QtCore import Qt, QByteArray, QBuffer, QIODevice
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QImage, QPixmap

from shibokensupport import feature # type: ignore[import-not-found]
feature.set_selection(feature.snake_case | feature.true_property)
assert 'snake_case' in feature.info() and 'true_property' in feature.info()

import json
from typing import Self, Dict, Any, List
import ast
from io import BytesIO
import os

from .base import LibraryStrategy, ImageGeneratorStrategy
from ..config import BaseConfig, TestConfig, DefaultConfig
from ..adapters import QtMetadataAdapter
from ..utils import MetadataOrganizer as mdo, MetadataSerializer as mds


class QtStrategy(LibraryStrategy):
    """
    Stratégie concrète de gestion des métadonnées pour la bibliothèque Qt.

    Gère l'introspection des composants PySide6 disponibles et expose leurs
    métadonnées structurées pour la construction du graphe nodal. Les métadonnées
    sont générées à la demande et mises en cache pour éviter les introspections
    répétées.

    Attributes:
        _name (str): Le nom de la bibliothèque, toujours 'qt'.
        _language (str): Le langage associé, toujours 'python'.
        __app (QApplication): L'instance de l'application Qt offscreen.
        __all_meta_objects (dict): Le cache des métadonnées générées.
        __config (BaseConfig): La configuration déterminant les composants
            à introspecter.
    """
    def __init__(self:Self, config : BaseConfig = DefaultConfig()) -> None:
        """
        Initialise la stratégie Qt avec une configuration.

        Args:
            config (BaseConfig): La configuration déterminant les composants
                PySide6 à introspecter. Par défaut `TestConfig`.

        Raises:
            ValueError: Si aucune configuration n'est fournie.
        """
        if not config:
            raise ValueError("QtStrategy a besoin d'une instance ")
        self._name = "qt"
        self._language = "python"

        self.__app = None

        self.__all_meta_objects = None

        self.__config = config

    @property
    def name(self:Self) -> str:
        """
        Le nom identifiant la bibliothèque graphique.

        Returns:
            str: Toujours 'qt'.
        """
        return self._name
    
    @property
    def language(self:Self) -> str:
        """
        Le nom du langage associé à cette stratégie.

        Returns:
            str: Toujours 'python'.
        """
        return self._language
    
    @property
    def metadata(self: Self) -> Dict[str, Any]:
        """
        Les métadonnées des composants Qt disponibles.

        Si les métadonnées ne sont pas encore générées, l'introspection est
        déclenchée silencieusement via `update_meta_objects`.

        Returns:
            Dict[str, Any]: Le dictionnaire des métadonnées des composants PySide6.
        """
        if self.__all_meta_objects == None:
            self.update_meta_objects()
        return self.__all_meta_objects

    def get_meta_objects(self:Self) -> Dict[str, Any]:
        """
        Retourne les métadonnées des composants Qt structurées pour l'interface visuelle.

        Si les métadonnées ne sont pas encore générées, l'introspection est
        déclenchée silencieusement. Les métadonnées sont organisées, restructurées
        et sauvegardées sur disque avant d'être retournées.

        Returns:
            Dict[str, Any]: Un dictionnaire organisé cataloguant les classes, widgets
                et propriétés disponibles pour la construction du graphe nodal.
        """
        if self.__all_meta_objects == None:
            self.update_meta_objects()

        serialized_dict = mdo.organize_dict(self.__all_meta_objects, "direct_parent")
        serialized_dict = mds.restructure_dict(serialized_dict)
        self.__create_data_file(serialized_dict, "./core/data/all_meta_objects.json")
        return serialized_dict
    
    def update_meta_objects(self:Self) -> Dict[str, Any]:
        """
        Déclenche l'introspection des composants PySide6 et met à jour le cache.

        Force la régénération des métadonnées même si elles sont déjà en cache,
        ce qui est utile lorsque la configuration a changé.

        Returns:
            Dict[str, Any]: Le dictionnaire brut des métadonnées générées.
        """
        self.__all_meta_objects = {}
        self.__generate_meta_objects(self.__all_meta_objects)

        return self.__all_meta_objects  

    def __generate_meta_objects(self:Self, object_dict:Dict[str, Any]) -> None:
        """
        Introspecte les composants PySide6 et peuple le dictionnaire de métadonnées.

        Méthode interne destinée à être appelée par `update_meta_objects`. Instancie
        une `QApplication` offscreen si nécessaire, puis itère sur les composants
        définis dans la configuration pour extraire leurs métadonnées via
        `QtMetadataAdapter`.

        Args:
            object_dict (Dict[str, Any]): Le dictionnaire à peupler avec les
                métadonnées des composants.
        """
        self.__app = QApplication.instance()

        if not self.__app:
            self.__app = QApplication(["-platform", "offscreen"])

        for cls in self.__config.objects_implemented:
            meta = QtMetadataAdapter(cls, self.__config, recursive = True)
            object_dict[meta.class_name] = meta.to_dict()
    
    def __create_data_file(self:Self, object_dict:Dict[str, Any], path:str) -> None:
        """
        Sauvegarde les métadonnées dans un fichier JSON sur disque.

        Méthode interne destinée à être appelée par `get_meta_objects`. N'écrit
        le fichier que si le dossier de destination existe déjà.

        Args:
            object_dict (Dict[str, Any]): Les métadonnées à sauvegarder.
            path (str): Le chemin complet du fichier de destination.
        """
        dossier = os.path.dirname(path)
        if dossier and os.path.exists(dossier):
            with open(path, "w", encoding="utf-8") as file:
                json.dump(object_dict, file, indent=4, sort_keys=False)

class QtOffScreenGenerator(ImageGeneratorStrategy):
    """
    Moteur de rendu visuel offscreen pour les aperçus Qt.

    Compile un AST Python en code exécutable, instancie le widget Qt
    correspondant dans un environnement offscreen et capture son rendu
    sous forme d'image en mémoire.

    Attributes:
        _name (str): Le nom du générateur, toujours 'qt'.
        _output_format (str): Le format d'exportation de l'image (ex: 'PNG').
        _app (QApplication): L'instance de l'application Qt offscreen.
    """
    def __init__(self: Self, output_format: str = "PNG") -> None:
        """
        Initialise le générateur offscreen avec un format d'exportation.

        Instancie une `QApplication` offscreen si aucune n'est déjà active.

        Args:
            output_format (str): Le format d'exportation de l'image. Par défaut 'PNG'.

        Raises:
            TypeError: Si output_format n'est pas de type str.
        """
        self._name: str = "qt"
        self._output_format:str
        self.output_format = output_format

        self._app = QApplication.instance()
        if not self._app:
            self._app = QApplication(["-platform", "offscreen"])

    @property
    def name(self: Self) -> str:
        """
        Le nom identifiant le générateur d'image.

        Returns:
            str: Toujours 'qt'.
        """
        return self._name

    @property
    def output_format(self:Self) -> str:
        """
        Le format d'exportation de l'image.

        La modification de cette propriété (via son setter) ajustera le format
        qui sera utilisé lors du prochain appel à `generate_preview`.

        Returns:
            str: Le format d'image actuel (ex: 'PNG', 'JPEG').

        Raises:
            TypeError: Si la valeur assignée n'est pas de type str.
        """
        return self._output_format
    
    @output_format.setter
    def output_format(self:Self, output_format:str):
        if not isinstance(output_format, str):
            raise TypeError("output_format doit être de type str.")
        
        self._output_format = output_format

    def generate_preview(self:Self, ast_root: ast.Module) -> BytesIO:
        GeneratedAppClass = self._compile_ast(ast_root)
        
        _, widget = self._generate_main_widget(GeneratedAppClass)

        pixmap = widget.grab()
        image = pixmap.to_image()
        
        return self._convert_to_buffer(image)
    
    def _compile_ast(self:Self, ast_root: ast.Module) -> type[QWidget]:
        """
        Compile un AST Python et retourne l'image du widget rendu en mémoire.

        Orchestre la séquence complète de rendu : compilation de l'AST,
        instanciation du widget Qt en offscreen, capture du rendu et conversion
        en flux d'octets.

        Args:
            ast_root (ast.Module): Le nœud racine de l'AST contenant la définition
                du widget à rendre.

        Returns:
            BytesIO: Un flux d'octets contenant l'image générée dans le format
                défini par `output_format`.

        Raises:
            ValueError: Si la classe `MyApp` n'est pas trouvée dans l'AST compilé.
        """
        compiled_code = compile(ast_root, filename="<syntaxnode_ast>", mode="exec")
        exec_env = globals().copy()
        exec(compiled_code, exec_env)
        
        if 'MyApp' not in exec_env:
            raise ValueError("La classe MyApp n'a pas été trouvée dans l'AST.")
            
        return exec_env['MyApp']
    
    def _generate_main_widget(self: Self, main_widget:type[QWidget]) -> tuple[QWidget, QWidget]:
        """
        Instancie le widget principal et retourne le widget cible à capturer.

        Méthode interne destinée à être appelée par `generate_preview`. Configure
        le widget pour un rendu offscreen et détermine le widget cible — soit
        `my_widget` s'il est défini, soit le widget racine lui-même.

        Args:
            main_widget (type[QWidget]): La classe du widget principal à instancier.

        Returns:
            tuple[QWidget, QWidget]: Un tuple contenant le widget racine et le
                widget cible à capturer.
        """
        root_widget = main_widget()
        
        root_widget.set_attribute(Qt.WidgetAttribute.WA_DontShowOnScreen)
        
        root_widget.adjust_size()

        if hasattr(root_widget, "my_widget"):
            widget = root_widget.my_widget
        else:
            widget = root_widget

        return root_widget, widget
    
    def _convert_to_buffer(self:Self, image: QImage) -> BytesIO:
        """
        Convertit une image Qt en flux d'octets en mémoire.

        Méthode interne destinée à être appelée par `generate_preview`. Écrit
        l'image dans un buffer Qt intermédiaire avant de le transférer dans
        un `BytesIO`.

        Args:
            image (QImage): L'image Qt à convertir.

        Returns:
            BytesIO: Un flux d'octets contenant l'image dans le format défini
                par `output_format`.
        """
        byte_array = QByteArray()
        qt_buffer = QBuffer(byte_array)
        qt_buffer.open(QIODevice.WriteOnly)
        image.save(qt_buffer, self.output_format)
        
        return BytesIO(byte_array.data())
        