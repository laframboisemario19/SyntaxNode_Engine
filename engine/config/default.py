"""
Configuration standard pour les composants Qt dans le moteur SyntaxNode.

Ce module fournit la classe `DefaultConfig`, qui définit l'ensemble complet
des composants PySide6, des types de propriétés et des paramètres supportés
pour un usage en production.

Classes
-------
DefaultConfig: Configuration standard pour un usage en production avec Qt/PySide6.
"""

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

from typing import Any, Dict, Tuple

from .base import BaseConfig


class DefaultConfig(BaseConfig):
    """
    Configuration standard pour un usage en production avec Qt/PySide6.

    Définit un ensemble étendu de composants PySide6 (widgets, layouts),
    de types complexes (QFont, QColor, QSizePolicy), d'énumérations et de
    flags Qt disponibles pour l'introspection et la génération de code.

    Attributes:
        __objects_implemented (Tuple[type, ...]): Les classes de composants
            graphiques supportées.
        __primitives_types (Tuple[type, ...]): Les types primitifs supportés.
        __complex_types_implemented (Dict[type, Any]): Les types complexes
            Qt supportés avec leur description de sérialisation.
        __enum_implemented (Tuple[type, ...]): Les types d'énumération Qt
            supportés.
        __flags_implemented (Tuple[type, ...]): Les types de flags Qt supportés.
        __params_implemented (Tuple[str, ...]): Les noms de propriétés supportées.
        __type_map (Dict[str, type]): La table de correspondance des types.
    """

    def __init__(self) -> None:
        """Initialise la configuration avec l'ensemble complet des types et composants Qt."""
        self.__objects_implemented = (QObject, QWidget, QAbstractButton, QPushButton, QHBoxLayout, QLayout, QBoxLayout, QVBoxLayout, QFrame,
                                      QLabel, QLineEdit, QCheckBox, QAbstractSlider, QSlider, QGroupBox, QComboBox, QAbstractSpinBox, QSpinBox, QProgressBar,
                                      QTextEdit, QFrame, QRadioButton, QDoubleSpinBox)

        self.__primitives_types = (int, str, bool, float)

        self.__complex_types_implemented = {QSizePolicy: ("QSizePolicy", {"horizontal_policy": QSizePolicy.Policy, "vertical_policy": QSizePolicy.Policy, "horizontal_stretch": int, "vertical_stretch": int}),
                                            QRect: ("QRect", {"x": int, "y": int, "width": int, "height": int}),
                                            QPoint: ("QPoint", {"x": int, "y": int}),
                                            QSize: ("QSize", {"width": int, "height": int}),
                                            QMargins: ("QMargins", {"left": int, "top": int, "right": int, "bottom": int}),
                                            QFont: ("QFont", {"family": str, "point_size": int, "weight": int, "italic": bool}),
                                            QColor: ("QColor", {"red": int, "green": int, "blue": int, "alpha": int})}

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

        self.__type_map = {_type.__name__: _type for _type in all_types}
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
    def objects_implemented(self) -> Tuple[type, ...]:
        """
        Les classes de composants graphiques supportées par cette configuration.

        Returns:
            Tuple[type, ...]: Les classes PySide6 instanciables et introspecables.
        """
        return self.__objects_implemented

    @property
    def primitives_types(self) -> Tuple[type, ...]:
        """
        Les types primitifs Python supportés pour les valeurs de propriétés.

        Returns:
            Tuple[type, ...]: Les types primitifs (int, str, bool, float).
        """
        return self.__primitives_types

    @property
    def complex_types_implemented(self) -> Dict[type, Any]:
        """
        Les types complexes Qt supportés et leur description de sérialisation.

        Returns:
            Dict[type, Any]: Les types complexes (QFont, QColor, QSizePolicy, etc.)
                associés à leur nom générique et leurs attributs.
        """
        return self.__complex_types_implemented

    @property
    def enum_implemented(self) -> Tuple[type, ...]:
        """
        Les types d'énumération Qt supportés pour les propriétés.

        Returns:
            Tuple[type, ...]: Les types d'énumération (Qt.FocusPolicy, etc.).
        """
        return self.__enum_implemented

    @property
    def flags_implemented(self) -> Tuple[type, ...]:
        """
        Les types de flags Qt supportés pour les propriétés.

        Returns:
            Tuple[type, ...]: Les types de flags (Qt.AlignmentFlag, etc.).
        """
        return self.__flags_implemented

    @property
    def params_implemented(self) -> Tuple[str, ...]:
        """
        Les noms de paramètres de propriétés supportés par cette configuration.

        Returns:
            Tuple[str, ...]: Les noms de propriétés en snake_case supportées.
        """
        return self.__params_implemented

    @property
    def type_map(self) -> Dict[str, type]:
        """
        La table de correspondance entre les noms de types C++/Qt et les types Python.

        Returns:
            Dict[str, type]: La table de correspondance des types.
        """
        return self.__type_map

    def is_param_supported(self, name: str) -> bool:
        """
        Vérifie si un nom de paramètre est supporté par cette configuration.

        Args:
            name (str): Le nom du paramètre en snake_case à vérifier.

        Returns:
            bool: True si le paramètre est dans `params_implemented`, False sinon.
        """
        return name in self.__params_implemented
