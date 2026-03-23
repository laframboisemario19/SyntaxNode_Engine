import sys

import PySide6
from __feature__ import snake_case, true_property # type: ignore[import-not-found]

from PySide6.QtCore import (QObject, QMetaObject, QMetaProperty, QMetaMethod)
from PySide6.QtWidgets import (QWidget, QLayout)

from shibokensupport import feature # type: ignore[import-not-found]
feature.set_selection(feature.snake_case | feature.true_property)
assert 'snake_case' in feature.info() and 'true_property' in feature.info()

from typing import Any

from .base import MetadataAdapter
from ..config import BaseConfig
from ..utils import MetadataSerializer as mds


class QtMetadataAdapter(MetadataAdapter):
    def __init__(self, cls:type, config:BaseConfig, recursive:bool = True):
        super().__init__(cls)
        self.__config = config

        self._meta = self.cls.staticMetaObject
        self._class_name = self._meta.class_name()
        self._category = self.__extract_category()
        self._module = self.cls.__module__

        self._parent_class = self._meta.super_class().class_name() if self._meta.super_class() else None

        self._obj = self._safe_instantiate()
        self._is_abstract = self._obj == None

        self._properties = self.__extract_properties(recursive)
        self._methods = self.__extract_methods(recursive)

    @property
    def meta(self) -> QMetaObject:
        return self._meta

    @property
    def class_name(self) -> str:
        return self._class_name
    
    @property
    def category(self) -> str:
        return self._category
    
    @property
    def parent_class(self) -> str:
        return self._parent_class
    
    @property
    def module(self) -> str:
        return self._module

    @property
    def is_abstract(self) -> bool:
        return self._is_abstract

    @property
    def properties(self) -> dict[str, Any]:
        return self._properties

    @property
    def methods(self) -> dict[str, Any]:
        return self._methods

    def to_dict(self):
        data = {
            "category": self._category,
            "name": self._class_name,
            "module": self._module,
            "is_abstract": self._is_abstract,
            "property": self._properties,
            "method": self._methods
            }

        if self._parent_class:
            data["direct_parent"] = self._parent_class
        
        return data

    def _safe_instantiate(self) -> QObject:
        try:
            return self.cls()
        except Exception as e:
            return None

    def __extract_category(self) -> str:
        category = "widget" if issubclass(self.cls, QWidget) else "layout"
        if issubclass(self.cls, QObject) and not issubclass(self.cls, (QWidget, QLayout)):
            category = "core"
        return category
    
    def __extract_properties(self, recursive:bool = True) -> dict[str,Any]:
        offset = 0 if recursive else self._meta.property_offset()
        properties = {}
        for idx in range(offset, self._meta.property_count()):
        
            meta_property = self._meta.property(idx)

            property_type = self.__config.type_map.get(meta_property.type_name())
            property_name = mds.to_snake_case(meta_property.name())

            if property_type and self.__config.is_param_supported(property_name):
                processed_property = self.__process_type(property_type, meta_property)
                properties[property_name] = processed_property
                properties[property_name]["name"] = mds.to_snake_case(property_name)

        return properties
    
    def __process_type(self, property_type:type, meta_property:QMetaProperty) -> dict[str,Any]:
        processed_property = None
        if property_type in self.__config.primitives_types:
            processed_property = self.__process_primitive_type(meta_property, property_type)
        elif property_type in self.__config.complex_types_implemented:
            processed_property = self.__process_complex_type(meta_property, property_type)
        elif property_type in self.__config.enum_implemented:
            processed_property = self.__process_enum_type(meta_property, property_type)
        elif property_type in self.__config.flags_implemented:
            processed_property = self.__process_flag_type(meta_property, property_type)

        return processed_property
    
    def __process_primitive_type(self, q_meta_property:QMetaProperty, property_type:type) -> dict[str,Any]:
        property_type_name = property_type.__name__
        if not self._is_abstract :
            default_value = q_meta_property.read(self._obj)
            return {"type":property_type_name, "default":default_value}
        else:
            return {"type":property_type_name}

    def __process_complex_type(self, q_meta_property:QMetaProperty, property_type:type) -> dict[str,Any]:
        generic_name, attributes = self.__config.complex_types_implemented.get(property_type)
        data = {"type": generic_name, "module":property_type.__module__}

        if not self._is_abstract:
            value = {}
            
            complex_obj = q_meta_property.read(self._obj)
            if complex_obj:
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

    def __process_enum_type(self, q_meta_property:QMetaProperty, property_type:type) -> dict[str,Any]:
        type_name = "enum"
        options = list(property_type.__members__)

        if not self._is_abstract:
            enum = q_meta_property.read(self._obj)
            default = enum.name
            return {"type": type_name, "default": default, "options": options}
        else:
            return {"type": type_name, "options": options}
        
    def __process_flag_type(self, q_meta_property:QMetaProperty, property_type:type) -> dict[str,Any]:
        type_name = "flag"

        options = {"exclusive":{}, "non_exclusive":[]}
        mask = {}
        value_to_filter = {}

        for key, value in property_type._member_map_.items():
            if "Mask" in key:
                key = key.replace("_Mask", "")
                mask[key] = value.value
                options["exclusive"][key] = []
            else:
                value_to_filter[key] = value.value

        for key, value in value_to_filter.items():
            non_exclusive = True
            for k, m in mask.items():
                if m | value == m:
                    options["exclusive"][k].append(key)
                    non_exclusive = False
                elif m & value != 0:
                    non_exclusive = False
                    break
            if non_exclusive:
                options["non_exclusive"].append(key)

        if not self._is_abstract:
            default = {"exclusive": {}, "non_exclusive": []}

            flag = q_meta_property.read(self._obj)
            values = flag.name.split(sep = "|")

            for value in values:
                if value in options["non_exclusive"]:
                    default["non_exclusive"].append(value)
                else:
                    for category, collection in options["exclusive"].items():
                        if value in collection:
                            default["exclusive"][category] = value

            return {"type": type_name, "default": default, "options": options}
        else:
            return {"type": type_name, "options": options}

    def __extract_methods(self, recursive:bool = True) -> dict[str,Any]:
        offset = 0 if recursive else self._meta.method_offset()
        methods = {"signal":{}, "slot":{}}
        for idx in range(offset, self._meta.method_count()):
            meta_method = self._meta.method(idx)
            method_name = mds.to_snake_case(meta_method.name().data().decode())
            method_type = meta_method.method_type()
            parameters = []
            parameters_valid = True

            parameters, parameters_valid = self.__extract_params(meta_method)

            if not parameters_valid:
                continue
             
            if method_type == QMetaMethod.MethodType.Signal:
                method_type = "signal"
            elif method_type == QMetaMethod.MethodType.Slot:
                method_type = "slot"
            else:
                continue

            if method_name not in methods[method_type]:
                methods[method_type][method_name] = {}
                methods[method_type][method_name]["name"] = mds.to_snake_case(method_name)
                methods[method_type][method_name]["parameter"] = parameters
            
        return methods
    
    def __extract_params(self, meta_method:QMetaMethod) -> dict[str,Any]:
        parameters_valid = True
        parameters = []
        for idx, (name, param_type) in enumerate(zip(meta_method.parameter_names(), meta_method.parameter_types())):
            param_type = param_type.data().decode()
            param_type = mds.clean_cpp_params(param_type)

            param_type = self.__config.type_map.get(param_type)
            
            if not param_type:
                parameters_valid = False
                break

            module = param_type.__module__
            param_type = self.__get_type_name(param_type)

            name = mds.to_snake_case(name.data().decode())
            name = name if name != "" else "param_" + str(idx + 1)

            parameters.append({"type":param_type, "name":name})
            if module and module != "builtins":
                parameters[-1]["module"] = module
        return (parameters, parameters_valid)
    
    def __get_type_name(self, type_name:type) -> str | dict[str,Any]:
        if type_name in self.__config.primitives_types + self.__config.objects_implemented:
                type_name = type_name.__name__
        elif type_name in self.__config.complex_types_implemented:
            generic_name, attributes = self.__config.complex_types_implemented.get(type_name)
            data = {"type": generic_name}
            value = {}
            for attribute, attr_type in attributes.items():
                value[attribute] = {"type":attr_type.__name__} if attr_type not in self.__config.enum_implemented else {"type" : "enum"}
            data["value"] = value
            type_name = data
        elif type_name in self.__config.enum_implemented:
            type_name = "enum"
        
        return type_name