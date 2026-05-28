import sys

import PySide6
from __feature__ import snake_case, true_property # type: ignore[import-not-found]

from PySide6.QtCore import (Qt, QObject, QMargins, QRect, QPoint, QSize)
from PySide6.QtGui import (QColor, QFont)
from PySide6.QtWidgets import (QWidget, QPushButton, QAbstractButton, QLayout, QBoxLayout, QVBoxLayout, QHBoxLayout,
                               QFrame, QLabel, QSizePolicy, QLineEdit, QCheckBox, QAbstractSlider, QSlider, QGroupBox, 
                               QComboBox, QAbstractSpinBox, QSpinBox, QProgressBar, QTextEdit, QRadioButton, QDoubleSpinBox)

from shibokensupport import feature # type: ignore[import-not-found]
feature.set_selection(feature.snake_case | feature.true_property)
assert 'snake_case' in feature.info() and 'true_property' in feature.info()

import json as json

from .base import BaseConfig

class DefaultConfig(BaseConfig):
    def __init__(self):
        self.__objects_implemented = (QObject, QWidget, QAbstractButton, QPushButton, QHBoxLayout, QLayout, QBoxLayout, QVBoxLayout, QFrame, 
                                      QLabel, QLineEdit, QCheckBox, QAbstractSlider, QSlider, QGroupBox, QComboBox, QAbstractSpinBox, QSpinBox, QProgressBar,
                                      QTextEdit, QFrame, QRadioButton, QDoubleSpinBox)
        
        self.__primitives_types = (int, str, bool, float)
        
        self.__complex_types_implemented = {QSizePolicy: ("QSizePolicy", {"horizontal_policy":QSizePolicy.Policy, "vertical_policy": QSizePolicy.Policy, "horizontal_stretch":int, "vertical_stretch":int}),
                                            QRect: ("QRect", {"x":int, "y":int, "width":int, "height":int}),
                                            QPoint: ("QPoint", {"x":int, "y":int}),
                                            QSize: ("QSize", {"width":int, "height":int}),
                                            QMargins: ("QMargins", {"left":int, "top":int, "right":int, "bottom":int}),
                                            QFont: ("QFont", {"family":str, "point_size":int, "weight":int, "italic":bool}),
                                            QColor: ("QColor", {"red":int, "green":int, "blue":int, "alpha":int})}
        
        self.__enum_implemented = (QSizePolicy.Policy, Qt.FocusPolicy, Qt.ContextMenuPolicy, Qt.LayoutDirection, QFrame.Shape, 
                                   QFrame.Shadow, Qt.TextFormat, QLayout.SizeConstraint, QLineEdit.EchoMode, Qt.Orientation,
                                   QTextEdit.LineWrapMode, Qt.ScrollBarPolicy)
        
        self.__flags_implemented = (Qt.AlignmentFlag, Qt.InputMethodHint, Qt.TextInteractionFlag)

        Qt.AlignmentFlag._value2member_map_

        self.__params_implemented = ("object_name", "text", "placeholder_text", "title", "checkable", "checked", "current_text", "current_index",
            "minimum", "maximum", "value", "single_step", "prefix", "suffix", "text_visible", "format", "accepts_rich_text", "text_format", 
            "text_interaction_flags", "word_wrap", "scaled_contents", "alignment", "indent", "margin", "echo_mode", "read_only", "max_length",
            "line_wrap_mode", "horizontal_scroll_bar_policy", "geometry", "minimum_size", "maximum_size", "minimum_width", "minimum_height",
            "maximum_width", "maximum_height", "size_policy", "style_sheet", "font", "frame_shape", "frame_shadow", "line_width", "orientation",
            "enabled", "visible", "focus_policy", "context_menu_policy", "layout_direction", "window_opacity", "window_title", "spacing", "contents_margins", 
            "size_constraint")

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
            "QFlags<Qt::TextInteractionFlag>": Qt.TextInteractionFlag,
            "QLineEdit::EchoMode": QLineEdit.EchoMode,
            "Qt::Orientation": Qt.Orientation,
            "QTextEdit::LineWrapMode": QTextEdit.LineWrapMode,
            "Qt::ScrollBarPolicy": Qt.ScrollBarPolicy

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