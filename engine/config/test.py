import sys

import PySide6
from __feature__ import snake_case, true_property # type: ignore[import-not-found]

from PySide6.QtCore import (Qt, QObject, QMargins, QRect, QPoint, QSize)
from PySide6.QtGui import (QColor, QFont)
from PySide6.QtWidgets import (QWidget, QPushButton, QAbstractButton, QLayout, QBoxLayout, QVBoxLayout, 
                               QFrame, QLabel, QSizePolicy)

from shibokensupport import feature # type: ignore[import-not-found]
feature.set_selection(feature.snake_case | feature.true_property)
assert 'snake_case' in feature.info() and 'true_property' in feature.info()

import json as json

class TestConfig():
    def __init__(self):
        self.__objects_implemented = (QObject, QWidget, QAbstractButton, QPushButton, QLayout, QBoxLayout, QVBoxLayout, QFrame, 
                                      QLabel)
        self.__primitives_types = (int, str, bool, float)
        
        self.__complex_types_implemented = {QSizePolicy: ("QSizePolicy", {"horizontal_policy":QSizePolicy.Policy, "vertical_policy": QSizePolicy.Policy, "horizontal_stretch":int, "vertical_stretch":int}),
                                            QRect: ("QRect", {"x":int, "y":int, "width":int, "height":int}),
                                            QPoint: ("QPoint", {"x":int, "y":int}),
                                            QSize: ("QSize", {"width":int, "height":int}),
                                            QMargins: ("QMargins", {"left":int, "top":int, "right":int, "bottom":int}),
                                            QFont: ("QFont", {"family":str, "point_size":int, "weight":int, "italic":bool}),
                                            QColor: ("QColor", {"red":int, "green":int, "blue":int, "alpha":int})}
        
        self.__enum_implemented = (QSizePolicy.Policy, Qt.FocusPolicy, Qt.ContextMenuPolicy, Qt.LayoutDirection, QFrame.Shape, 
                                   QFrame.Shadow, Qt.TextFormat, QLayout.SizeConstraint)
        self.__flags_implemented = (Qt.AlignmentFlag, Qt.InputMethodHint, Qt.TextInteractionFlag)

        Qt.AlignmentFlag._value2member_map_

        self.__params_implemented = ("enabled", "geometry", "pos", "frame_size", "size", "alignment", "object_name",
                                     "rect", "children_rect", "size_policy", "minimum_size", "maximum_size", "minimum_width", 
                                     "minimum_height", "maximum_width", "maximum_height", "font", "focus_policy", "focus", 
                                     "context_menu_policy", "visible", "full_screen", "window_title", "window_opacity", "layout_direction",
                                     "text", "checkable", "checked", "frame_shape", "frame_shadow", "line_width", "mid_line_width",
                                     "frame_rect", "text_format", "scaled_contents", "word_wrap", "margin", "indent",
                                     "has_selected_text", "selected_text", "spacing", "contents_margins", "size_constraint", "horizontal_size_constraint",
                                     "vertical_size_constraint", "input_method_hints", "text_interaction_flags")

        all_types = (self.__objects_implemented + 
                    self.__primitives_types + 
                    tuple(self.__complex_types_implemented.keys()) + 
                    self.__enum_implemented +
                    self.__flags_implemented)

        self.__type_map = {_type.__name__ : _type for _type in all_types}
        self.__type_map.update({
            "QString": str,
            "Qt::FocusPolicy": Qt.FocusPolicy,
            "Qt::ContextMenuPolicy": Qt.ContextMenuPolicy,
            "double": float,
            "Qt::LayoutDirection": Qt.LayoutDirection,
            "QFrame::Shape": QFrame.Shape,
            "QFrame::Shadow": QFrame.Shadow,
            "Qt::TextFormat": Qt.TextFormat,
            "QLayout::SizeConstraint": QLayout.SizeConstraint,
            "QFlags<Qt::InputMethodHint>": Qt.InputMethodHint,
            "QFlags<Qt::AlignmentFlag>": Qt.AlignmentFlag,
            "QFlags<Qt::TextInteractionFlag>": Qt.TextInteractionFlag
        })

    @property
    def objects_implemented(self):
        return self.__objects_implemented
    
    @property
    def primitives_types(self):
        return self.__primitives_types
    
    @property
    def complex_types_implemented(self):
        return self.__complex_types_implemented
    
    @property
    def enum_implemented(self):
        return self.__enum_implemented
    
    @property
    def flags_implemented(self):
        return self.__flags_implemented
    
    @property
    def params_implemented(self):
        return self.__params_implemented
    
    @property
    def type_map(self):
        return self.__type_map
    
    def is_param_supported(self, name:str) -> bool:
        return name in self.__params_implemented