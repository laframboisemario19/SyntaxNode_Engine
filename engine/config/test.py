"""
Configuration minimale pour les tests avec Qt/PySide6.

Ce module fournit la classe `TestConfig`, qui définit un sous-ensemble
réduit des composants PySide6 et des types de propriétés supportés,
destiné aux tests et au développement.

Classes
-------
TestConfig: Configuration minimale pour les tests et le développement.
"""

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

from typing import Any, Dict, Tuple

from .base import BaseConfig


class TestConfig(BaseConfig):
    """
    Configuration minimale pour les tests et le développement.

    Définit un sous-ensemble réduit des composants PySide6 (widgets de base,
    layouts) et des types de propriétés supportés, permettant une introspection
    plus rapide lors des tests unitaires et du développement.

    Attributes:
        __objects_implemented (Tuple[type, ...]): Les classes de composants
            graphiques supportées dans cette configuration minimale.
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
        """Initialise la configuration avec le sous-ensemble minimal de types et composants Qt."""
        self.__objects_implemented = (QObject, QWidget, QAbstractButton, QPushButton, QLayout, QBoxLayout, QVBoxLayout, QFrame,
                                      QLabel)
        self.__primitives_types = (int, str, bool, float)

        self.__complex_types_implemented = {QSizePolicy: ("QSizePolicy", {"horizontal_policy": QSizePolicy.Policy, "vertical_policy": QSizePolicy.Policy, "horizontal_stretch": int, "vertical_stretch": int}),
                                            QRect: ("QRect", {"x": int, "y": int, "width": int, "height": int}),
                                            QPoint: ("QPoint", {"x": int, "y": int}),
                                            QSize: ("QSize", {"width": int, "height": int}),
                                            QMargins: ("QMargins", {"left": int, "top": int, "right": int, "bottom": int}),
                                            QFont: ("QFont", {"family": str, "point_size": int, "weight": int, "italic": bool}),
                                            QColor: ("QColor", {"red": int, "green": int, "blue": int, "alpha": int})}

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
            "QFlags<Qt::TextInteractionFlag>": Qt.TextInteractionFlag
        })

    @property
    def objects_implemented(self) -> Tuple[type, ...]:
        """
        Les classes de composants graphiques supportées par cette configuration.

        Returns:
            Tuple[type, ...]: Le sous-ensemble minimal de classes PySide6
                instanciables et introspecables.
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
