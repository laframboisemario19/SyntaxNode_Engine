import sys

import PySide6
from __feature__ import snake_case, true_property # type: ignore[import-not-found]

from PySide6.QtCore import (Qt, QMetaObject, QObject, QMetaProperty, QMetaMethod, QMargins, QRect, QPoint, QSize)
from PySide6.QtGui import (QPaintDevice, QColor, QFont)
from PySide6.QtWidgets import (QWidget, QApplication, QPushButton, QAbstractButton, QLayout, QBoxLayout, QVBoxLayout, 
                               QFrame, QLabel, QSizePolicy)

from shibokensupport import feature # type: ignore[import-not-found]
feature.set_selection(feature.snake_case | feature.true_property)
assert 'snake_case' in feature.info() and 'true_property' in feature.info()

import json as json
import re

from .librairy_s import LibrairyStrategy
from .config.qt_config import QtConfig

class QtStrategy(LibrairyStrategy):
    def __init__(self):
        self._name = "qt"
        self._language = "python"

        self.__app = None

        self.__all_meta_objects = None

        self.__config = QtConfig()

    @property
    def name(self):
        return self._name
    
    @property
    def language(self):
        return self._language

    def get_meta_objects(self):
        if self.__all_meta_objects == None:
            self.update_meta_objects()

        return self.__all_meta_objects
    
    def update_meta_objects(self):
        meta_objects = {}
        self.__generate_meta_objects(meta_objects)
        self.__all_meta_objects = self.__organize_dict(meta_objects)
        self.__create_data_file(self.__all_meta_objects, "./data/all_meta_objects.json")

    def __generate_meta_objects(self, object_dict):
        if not self.__app:
            self.__app = QApplication()

        for element in self.__config.objects_implemented:
            meta = element.staticMetaObject
            name = meta.class_name()
            obj = self.__safe_instantiate(element)

            category = self.__get_category(element)

            object_dict[name] = {"category": category}

            super_class = meta.super_class()
            if super_class != None:
                object_dict[name]["direct_parent"] = super_class.class_name()
            
            object_dict[name]["is_abstract"] = obj == None
            object_dict[name]["property"] = self.__get_properties(obj, meta)
            object_dict[name]["method"] = self.__get_methods(meta)


    def __to_snake_case(self, text):
        ## Pour la regex : https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case 
        return re.sub(r'(?<!^)(?=[A-Z])', '_', text).lower()
    
    def __safe_instantiate(self, element):
        try:
            return element()
        except Exception as e:
            return None
        
    def __get_category(self, element):
        category = "widget" if issubclass(element, QWidget) else "layout"
        if issubclass(element, QObject) and not issubclass(element, (QWidget, QLayout)):
            category = "core"
        return category
    
    def __get_methods(self, meta):
        methods = {"signal":{}, "slot":{}}
        for idx in range(meta.method_count()):
            meta_method = meta.method(idx)
            method_name = self.__to_snake_case(meta_method.name().data().decode())
            method_type = meta_method.method_type()
            parameters = []
            parameters_valid = True

            parameters, parameters_valid = self.__get_params(meta_method)

            if not parameters_valid:
                continue

            if method_type == QMetaMethod.MethodType.Signal and method_name not in methods["signal"]:
                methods["signal"][method_name] = {}
                methods["signal"][method_name]["parameter"] = parameters
            elif method_type == QMetaMethod.MethodType.Slot and method_name not in methods["slot"]:
                methods["slot"][method_name] = {} 
                methods["slot"][method_name]["parameter"] = parameters
            
        return methods
    
    def __get_params(self, meta_method):
        parameters_valid = True
        parameters = []
        for idx, (name, param_type) in enumerate(zip(meta_method.parameter_names(), meta_method.parameter_types())):
            param_type = param_type.data().decode()
            param_type = re.sub(r'[*&]', '', param_type)
            param_type = self.__config.type_map.get(param_type)
            if param_type is None:
                parameters_valid = False
                break

            param_type = self.__get_type_name(param_type)

            name = self.__to_snake_case(name.data().decode())
            name = name if name != "" else "param_" + str(idx + 1)

            parameters.append({"type":param_type, "name":name})
        return (parameters, parameters_valid)

    def __get_type_name(self, type_name):
        if type_name in self.__config.primitives_types + self.__config.objects_implemented:
                type_name = type_name.__name__
        elif type_name in self.__config.complex_types_implemented:
            generic_name, attributes = self.__config.complex_types_implemented.get(type_name)
            data = {"type": generic_name}
            value = {}
            for attribute, type in attributes.items():
                value[attribute] = {"type":type.__name__} if type not in self.__config.enum_implemented else {"type" : "enum"}
            data["value"] = value
            type_name = data
        elif type_name in self.__config.enum_implemented:
            type_name = "enum"
        
        return type_name
    
    def __get_properties(self, obj, meta):
        # offset = meta.property_offset()
        properties = {}
        # for idx in range(offset, meta.property_count()):
        for idx in range(meta.property_count()):
        
            meta_property = meta.property(idx)
            property_type = self.__config.type_map.get(meta_property.type_name())
            property_name = self.__to_snake_case(meta_property.name())

            if property_type != None and property_name in self.__config.params_implemented:
                if property_type in self.__config.primitives_types:
                    processed_property = self.__process_primitive_type(obj, meta_property, property_type)
                elif property_type in self.__config.complex_types_implemented:
                    processed_property = self.__process_complex_type(obj, meta_property, property_type)
                elif property_type in self.__config.enum_implemented:
                    processed_property = self.__process_enum_type(obj, meta_property, property_type)
                elif property_type in self.__config.flags_implemented:
                    processed_property = self.__process_flag_type(obj, meta_property, property_type)
                properties[property_name] = processed_property
        return properties
                    

    def __process_primitive_type(self, obj, q_meta_property, property_type):
        property_type_name = property_type.__name__
        if obj != None:
            default_value = q_meta_property.read(obj)
            return {"type":property_type_name, "default":default_value}
        else:
            return {"type":property_type_name}

    def __process_complex_type(self, obj, q_meta_property, property_type):
        generic_name, attributes = self.__config.complex_types_implemented.get(property_type)
        data = {"type": generic_name}

        if obj != None:
            value = {}
            
            complex_obj = q_meta_property.read(obj)
            for attribute, type in attributes.items():
                method = getattr(complex_obj, attribute)
                default = method() if callable(method) else method
                value[attribute] = {"type":type.__name__, "default":default}
                
                if type in self.__config.enum_implemented:
                    
                    default = default.name

                    value[attribute]["type"] = "enum"
                    value[attribute]["default"] = default
                    value[attribute]["options"] = list(type.__members__)


            data["value"] = value

        return data

    def __process_enum_type(self, obj, q_meta_property, property_type):
        type_name = "enum"
        options = list(property_type.__members__)

        if obj != None:
            enum = q_meta_property.read(obj)
            default = enum.name
            return {"type": type_name, "default": default, "options": options}
        else:
            return {"type": type_name, "options": options}

    def __process_flag_type(self, obj, q_meta_property, property_type):
        type_name = "flag"
        options = list(property_type.__members__)

        if obj != None:
            flag = q_meta_property.read(obj)
            default = flag.name.split(sep = "|")
            return {"type": type_name, "default": default, "options": options}
        else:
            return {"type": type_name, "options": options}

    def __organize_dict(self, object_dict):
        root_objects = []

        for name, data in object_dict.items():
            parent_name = data.get("direct_parent")
            if parent_name and parent_name in object_dict:
                object_dict[parent_name][name] = data
            else :
                root_objects.append(name)

        for name, data in object_dict.items():
            if "direct_parent" in data:
                del data["direct_parent"]

        return {name : object_dict[name] for name in root_objects}
    
    def __create_data_file(self, object_dict, path):
        with open(path, "w", encoding="utf-8") as file:
            json.dump(object_dict, file, indent=4, sort_keys=False)
