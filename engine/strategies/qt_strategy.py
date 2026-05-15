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
from typing import Self
import ast
from io import BytesIO
import os

from .base import LibraryStrategy, ImageGeneratorStrategy
from ..config import BaseConfig, TestConfig
from ..adapters import QtMetadataAdapter
from ..utils import MetadataOrganizer as mdo, MetadataSerializer as mds


class QtStrategy(LibraryStrategy):
    def __init__(self, config : BaseConfig = TestConfig):
        if not config:
            raise ValueError("QtStrategy a besoin d'une instance ")
        self._name = "qt"
        self._language = "python"

        self.__app = None

        self.__all_meta_objects = None

        self.__config = config

    @property
    def name(self):
        return self._name
    
    @property
    def language(self):
        return self._language
    
    @property
    def metadata(self):
        if self.__all_meta_objects == None:
            self.update_meta_objects()
        return self.__all_meta_objects

    def get_meta_objects(self):
        if self.__all_meta_objects == None:
            self.update_meta_objects()

        serialized_dict = mdo.organize_dict(self.__all_meta_objects, "direct_parent")
        serialized_dict = mds.restructure_dict(serialized_dict)
        self.__create_data_file(serialized_dict, "./data/all_meta_objects.json")
        return serialized_dict
    
    def update_meta_objects(self):
        self.__all_meta_objects = {}
        self.__generate_meta_objects(self.__all_meta_objects)

        return self.__all_meta_objects  

    def __generate_meta_objects(self, object_dict):
        self.__app = QApplication.instance()

        if not self.__app:
            self.__app = QApplication(["-platform", "offscreen"])

        for cls in self.__config.objects_implemented:
            meta = QtMetadataAdapter(cls, self.__config, recursive = True)
            object_dict[meta.class_name] = meta.to_dict()
    
    def __create_data_file(self, object_dict, path):
        dossier = os.path.dirname(path)
        if dossier and os.path.exists(dossier):
            with open(path, "w", encoding="utf-8") as file:
                json.dump(object_dict, file, indent=4, sort_keys=False)

class QtOffScreenGenerator(ImageGeneratorStrategy):
    def __init__(self: Self, output_format: str = "PNG"):
        self._name: str = "qt"
        self._output_format:str
        self.output_format = output_format

        self._app = QApplication.instance()
        if not self._app:
            self._app = QApplication(["-platform", "offscreen"])

    @property
    def name(self: Self) -> str:
        return self._name

    @property
    def output_format(self:Self) -> str:
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
        compiled_code = compile(ast_root, filename="<syntaxnode_ast>", mode="exec")
        exec_env = globals().copy()
        exec(compiled_code, exec_env)
        
        if 'MyApp' not in exec_env:
            raise ValueError("La classe MyApp n'a pas été trouvée dans l'AST.")
            
        return exec_env['MyApp']
    
    def _generate_main_widget(self: Self, main_widget:type[QWidget]) -> QWidget:
        root_widget = main_widget()
        
        # root_widget.ensure_polished()
        root_widget.set_attribute(Qt.WidgetAttribute.WA_DontShowOnScreen)
        # root_widget.show()
        
        # self._app.process_events()
        
        root_widget.adjust_size()

        if hasattr(root_widget, "my_widget"):
            widget = root_widget.my_widget
        else:
            widget = root_widget

        return root_widget, widget
    
    def _convert_to_buffer(self, image: QImage) -> BytesIO:
        byte_array = QByteArray()
        qt_buffer = QBuffer(byte_array)
        qt_buffer.open(QIODevice.WriteOnly)
        image.save(qt_buffer, self.output_format)
        
        return BytesIO(byte_array.data())
        