import sys

import PySide6
from __feature__ import snake_case, true_property # type: ignore[import-not-found]

from PySide6.QtWidgets import QApplication

from shibokensupport import feature # type: ignore[import-not-found]
feature.set_selection(feature.snake_case | feature.true_property)
assert 'snake_case' in feature.info() and 'true_property' in feature.info()

import json

from .base import LibraryStrategy
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

    def get_meta_objects(self):
        if self.__all_meta_objects == None:
            self.update_meta_objects()

        serialized_dict = mds.restructure_dict(self.__all_meta_objects)
        self.__create_data_file(serialized_dict, "./data/all_meta_objects.json")
        return serialized_dict
    
    def update_meta_objects(self):
        meta_objects = {}
        self.__generate_meta_objects(meta_objects)

        self.__all_meta_objects = mdo.organize_dict(meta_objects, "direct_parent")

        return self.__all_meta_objects  

    def __generate_meta_objects(self, object_dict):
        if not self.__app:
            self.__app = QApplication()

        for cls in self.__config.objects_implemented:
            meta = QtMetadataAdapter(cls, self.__config, recursive = True)
            object_dict[meta.class_name] = meta.to_dict()
    
    def __create_data_file(self, object_dict, path):
        with open(path, "w", encoding="utf-8") as file:
            json.dump(object_dict, file, indent=4, sort_keys=False)
