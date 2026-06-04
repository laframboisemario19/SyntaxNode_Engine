"""
Adaptateur de métadonnées pour la bibliothèque Qt/PySide6.

Ce module fournit la classe `QtMetadataAdapter`, qui implémente le contrat
`MetadataAdapter` pour extraire et sérialiser les métadonnées des composants
PySide6 (propriétés, signaux, slots) via le système de métaobjet Qt (QMetaObject).

Classes
-------
QtMetadataAdapter: Adaptateur concret d'extraction des métadonnées Qt/PySide6.
"""

import sys

import PySide6
from __feature__ import snake_case, true_property # type: ignore[import-not-found]

from PySide6.QtCore import (QObject, QMetaObject, QMetaProperty, QMetaMethod)
from PySide6.QtWidgets import (QWidget, QLayout)

from shibokensupport import feature # type: ignore[import-not-found]
feature.set_selection(feature.snake_case | feature.true_property)
assert 'snake_case' in feature.info() and 'true_property' in feature.info()

from typing import Any, Dict, List, Optional, Tuple, Union

from .base import MetadataAdapter
from ..config import BaseConfig
from ..utils import MetadataSerializer as mds


class QtMetadataAdapter(MetadataAdapter):
    """
    Adaptateur concret d'extraction des métadonnées Qt/PySide6.

    Utilise le système de métaobjet Qt (QMetaObject) pour introspecter les
    propriétés inscriptibles et les méthodes (signaux, slots) d'une classe
    PySide6.

    Choix de design — QMetaObject plutôt que les outils Python natifs
    -----------------------------------------------------------------------
    Les approches Python natives comme `dir()` ou le module `inspect` ont été
    écartées pour les raisons suivantes :

    - `dir()` retourne une liste de noms Python sans contexte sémantique :
      impossible de distinguer une propriété Qt inscriptible d'un attribut Python
      ordinaire, une simple méthode d'un signal ou d'un slot, ni d'obtenir les
      types C++ originaux requis pour la table de correspondance (`type_map`).

    - `inspect` ignore le système de métaobjet Qt : les signaux apparaissent comme
      des objets `SignalInstance` opaques, les types des paramètres de slots ne
      sont pas exposés, et les propriétés Qt ne sont pas distinguables des
      descripteurs Python arbitraires.

    - `QMetaObject`, au contraire, expose le registre de métadonnées construit
      par le compilateur Qt (`moc`) à la compilation. Il donne accès aux noms
      de types C++ originaux (ex: `Qt::AlignmentFlag`), à l'état inscriptible
      de chaque propriété, aux noms et types précis des paramètres de signaux
      et de slots, à l'énumérateur associé à chaque propriété enum/flag, et
      à un offset de départ permettant de contrôler la profondeur d'héritage
      explorée (voir paramètre `recursive`).

    Choix de design — Instanciation temporaire pour les valeurs par défaut
    -----------------------------------------------------------------------
    Pour lire la valeur par défaut d'une propriété Qt, `QMetaProperty.read()`
    exige une instance concrète de la classe — il n'existe pas d'accès statique
    à ces valeurs dans le système Qt. La classe tente donc d'instancier chaque
    composant sans argument dans `_safe_instantiate`. En cas d'échec (classe
    abstraite ou constructeur incompatible), le composant est marqué abstrait
    et les propriétés sont extraites sans valeur par défaut.

    Choix de design — Paramètre `recursive`
    -----------------------------------------------------------------------
    Lorsque `recursive=True` (défaut), toutes les propriétés et méthodes
    héritées sont incluses, ce qui produit des métadonnées complètes et
    autonomes pour chaque composant. Lorsque `recursive=False`, l'extraction
    démarre à l'offset de la classe courante (via `property_offset()` et
    `method_offset()`), ne retournant que ce que la classe définit elle-même.
    Ce mode est utile pour construire une vue différentielle de la hiérarchie
    d'héritage, sans dupliquer les propriétés déjà documentées par les classes
    parentes.

    Attributes:
        _meta (QMetaObject): L'objet de métadonnées Qt de la classe.
        _class_name (str): Le nom de la classe (ex: 'QPushButton').
        _category (str): La catégorie du composant ('widget', 'layout' ou 'core').
        _module (str): Le module Python de la classe (ex: 'PySide6.QtWidgets').
        _parent_class (str | None): Le nom de la classe parente directe.
        _obj (QObject | None): L'instance temporaire pour l'extraction des
            valeurs par défaut, ou None si la classe est abstraite.
        _is_abstract (bool): True si la classe ne peut pas être instanciée.
        _properties (Dict[str, Any]): Les propriétés inscriptibles extraites.
        _methods (Dict[str, Any]): Les signaux et slots extraits.
    """

    def __init__(self, cls: type, config: BaseConfig, recursive: bool = True) -> None:
        """
        Initialise l'adaptateur et déclenche l'introspection complète de la classe.

        Args:
            cls (type): La classe PySide6 à introspecter.
            config (BaseConfig): La configuration déterminant les types et
                paramètres supportés.
            recursive (bool): Si True, inclut les propriétés et méthodes héritées.
                Si False, n'inclut que celles définies directement sur la classe,
                en utilisant les offsets de QMetaObject. Par défaut True.
        """
        super().__init__(cls)
        self.__config = config

        self._meta = self.cls.staticMetaObject
        self._class_name = self._meta.class_name()
        self._category = self.__extract_category()
        self._module = self.cls.__module__

        self._parent_class = self._meta.super_class().class_name() if self._meta.super_class() else None

        self._obj = self._safe_instantiate()
        self._is_abstract = self._obj is None

        self._properties = self.__extract_properties(recursive)
        self._methods = self.__extract_methods(recursive)

    @property
    def meta(self) -> QMetaObject:
        """
        L'objet de métadonnées Qt de la classe.

        Returns:
            QMetaObject: L'objet QMetaObject associé à la classe introspecée.
        """
        return self._meta

    @property
    def class_name(self) -> str:
        """
        Le nom de la classe du composant.

        Returns:
            str: Le nom de la classe (ex: 'QPushButton').
        """
        return self._class_name

    @property
    def category(self) -> str:
        """
        La catégorie du composant dans la hiérarchie Qt.

        Returns:
            str: La catégorie : 'widget', 'layout' ou 'core'.
        """
        return self._category

    @property
    def parent_class(self) -> str:
        """
        Le nom de la classe parente directe du composant.

        Returns:
            str: Le nom de la classe parente (ex: 'QAbstractButton').
        """
        return self._parent_class

    @property
    def module(self) -> str:
        """
        Le nom du module Python contenant la classe du composant.

        Returns:
            str: Le chemin du module (ex: 'PySide6.QtWidgets').
        """
        return self._module

    @property
    def is_abstract(self) -> bool:
        """
        Indique si la classe du composant est abstraite (non instanciable).

        Returns:
            bool: True si l'instanciation sans arguments a échoué, False sinon.
        """
        return self._is_abstract

    @property
    def properties(self) -> Dict[str, Any]:
        """
        Les propriétés inscriptibles du composant extraites via QMetaObject.

        Returns:
            Dict[str, Any]: Un dictionnaire des propriétés supportées, indexé
                par nom en snake_case.
        """
        return self._properties

    @property
    def methods(self) -> Dict[str, Any]:
        """
        Les signaux et slots du composant extraits via QMetaObject.

        Returns:
            Dict[str, Any]: Un dictionnaire organisé par type ('signal', 'slot'),
                chaque entrée contenant le nom et les paramètres de la méthode.
        """
        return self._methods

    def to_dict(self) -> Dict[str, Any]:
        """
        Sérialise les métadonnées du composant en un dictionnaire structuré.

        Returns:
            Dict[str, Any]: Un dictionnaire contenant la catégorie, le nom,
                le module, l'état abstrait, les propriétés et les méthodes du
                composant. La clé 'direct_parent' est ajoutée si la classe a
                une classe parente.
        """
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

    def _safe_instantiate(self) -> Optional[QObject]:
        """
        Tente d'instancier la classe sans arguments pour accéder aux valeurs par défaut.

        `QMetaProperty.read()` exige une instance concrète pour retourner la valeur
        courante d'une propriété — il n'existe pas d'accès statique à ces valeurs
        dans le système Qt. Si l'instanciation échoue (classe abstraite, constructeur
        requérant des arguments), le composant est marqué abstrait et les propriétés
        sont extraites sans valeur par défaut.

        Returns:
            Optional[QObject]: L'instance créée, ou None si l'instanciation échoue.
        """
        try:
            return self.cls()
        except Exception:
            return None

    def __extract_category(self) -> str:
        """
        Détermine la catégorie du composant selon sa hiérarchie d'héritage Qt.

        Utilise `issubclass` pour naviguer la hiérarchie Qt : QWidget (rendu
        visuel autonome), QLayout (gestionnaire de positionnement sans rendu
        propre) et QObject (objet de base non visuel). Les trois catégories
        sont mutuellement exclusives et couvrent l'ensemble des composants Qt.

        Returns:
            str: 'widget' si la classe hérite de QWidget, 'layout' si elle
                hérite de QLayout, 'core' pour tout autre QObject.
        """
        category = "widget" if issubclass(self.cls, QWidget) else "layout"
        if issubclass(self.cls, QObject) and not issubclass(self.cls, (QWidget, QLayout)):
            category = "core"
        return category

    def __extract_properties(self, recursive: bool = True) -> Dict[str, Any]:
        """
        Extrait les propriétés inscriptibles supportées via QMetaObject.

        Contrairement à `dir()` qui retourne tous les attributs Python sans
        distinction, `QMetaObject` permet d'itérer uniquement sur les
        propriétés déclarées avec `Q_PROPERTY` et de vérifier leur état
        inscriptible (`is_writable()`) ainsi que leur type C++ précis via
        `type_name()` — informations absentes du modèle d'introspection Python.

        Lorsque `recursive=False`, l'itération démarre à `property_offset()`
        pour n'inclure que les propriétés introduites par la classe courante,
        excluant celles déjà définies dans la hiérarchie parente.

        Args:
            recursive (bool): Si True, inclut les propriétés héritées (offset 0).
                Si False, commence à l'offset de la classe courante.

        Returns:
            Dict[str, Any]: Les propriétés inscriptibles supportées, indexées
                par nom en snake_case.
        """
        offset = 0 if recursive else self._meta.property_offset()
        properties = {}
        for idx in range(offset, self._meta.property_count()):
            meta_property = self._meta.property(idx)

            if meta_property.is_writable():
                property_type = self.__config.type_map.get(meta_property.type_name())
                property_name = mds.to_snake_case(meta_property.name())

                if property_type and self.__config.is_param_supported(property_name):
                    processed_property = self.__process_type(property_type, meta_property)
                    properties[property_name] = processed_property
                    properties[property_name]["name"] = mds.to_snake_case(property_name)

        return properties

    def __process_type(self, property_type: type, meta_property: QMetaProperty) -> Dict[str, Any]:
        """
        Délègue le traitement d'une propriété vers la méthode appropriée selon son type.

        Args:
            property_type (type): Le type Python correspondant à la propriété Qt.
            meta_property (QMetaProperty): L'objet QMetaProperty à traiter.

        Returns:
            Dict[str, Any]: Le dictionnaire décrivant la propriété sérialisée,
                ou None si le type n'est pas reconnu dans la configuration.
        """
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

    def __process_primitive_type(self, q_meta_property: QMetaProperty, property_type: type) -> Dict[str, Any]:
        """
        Sérialise une propriété de type primitif avec sa valeur par défaut.

        Lit la valeur actuelle de la propriété via `QMetaProperty.read()` sur
        l'instance temporaire. La propriété 'visible' est forcée à True pour
        éviter que les composants soient invisibles par défaut dans l'aperçu.

        Args:
            q_meta_property (QMetaProperty): L'objet QMetaProperty à traiter.
            property_type (type): Le type Python primitif de la propriété.

        Returns:
            Dict[str, Any]: Un dictionnaire avec les clés 'type' et 'default'
                (si le composant n'est pas abstrait).
        """
        property_type_name = property_type.__name__
        if not self._is_abstract:
            default_value = q_meta_property.read(self._obj) if q_meta_property.name() != "visible" else True
            return {"type": property_type_name, "default": default_value}
        else:
            return {"type": property_type_name}

    def __process_complex_type(self, q_meta_property: QMetaProperty, property_type: type) -> Dict[str, Any]:
        """
        Sérialise une propriété de type complexe Qt (ex: QFont, QColor, QSizePolicy).

        Les types complexes Qt encapsulent plusieurs attributs primitifs ou
        énumérations. Chaque attribut est extrait via son accesseur défini dans
        la configuration. Les attributs de type énumération reçoivent un
        traitement supplémentaire pour inclure leur namespace et leurs options.

        Args:
            q_meta_property (QMetaProperty): L'objet QMetaProperty à traiter.
            property_type (type): Le type Python complexe de la propriété.

        Returns:
            Dict[str, Any]: Un dictionnaire avec les clés 'type', 'module' et
                optionnellement 'value' (dictionnaire des attributs avec leurs
                valeurs par défaut).
        """
        generic_name, attributes = self.__config.complex_types_implemented.get(property_type)
        data = {"type": generic_name, "module": property_type.__module__}

        if not self._is_abstract:
            value = {}

            complex_obj = q_meta_property.read(self._obj)
            if complex_obj is not None:
                for attribute, attr_type in attributes.items():
                    method = getattr(complex_obj, attribute)
                    default = method() if callable(method) else method
                    value[attribute] = {"type": attr_type.__name__, "default": default}

                    if attr_type in self.__config.enum_implemented:
                        default = default.name
                        value[attribute]["type"] = "enum"
                        value[attribute]["namespace"] = [attr_type.__module__, *attr_type.__qualname__.split('.')]
                        value[attribute]["default"] = default
                        value[attribute]["options"] = list(attr_type.__members__)

                data["value"] = value

        return data

    def __process_enum_type(self, q_meta_property: QMetaProperty, property_type: type) -> Dict[str, Any]:
        """
        Sérialise une propriété de type énumération Qt.

        Exploite `QMetaProperty.enumerator()` pour extraire le namespace Qt
        précis de l'énumération — information inaccessible via `inspect` ou
        `dir()` qui retourneraient uniquement le type Python wrapper.

        Args:
            q_meta_property (QMetaProperty): L'objet QMetaProperty à traiter.
            property_type (type): Le type d'énumération Qt de la propriété.

        Returns:
            Dict[str, Any]: Un dictionnaire avec les clés 'type', 'options',
                'namespace' et optionnellement 'default' (si non abstrait).
        """
        type_name = "enum"
        options = list(property_type.__members__)
        namespace = self.__extract_namespace(q_meta_property, property_type)

        if not self._is_abstract:
            enum = q_meta_property.read(self._obj)
            default = enum.name
            return {"type": type_name, "default": default, "options": options, "namespace": namespace}
        else:
            return {"type": type_name, "options": options, "namespace": namespace}

    def __process_flag_type(self, q_meta_property: QMetaProperty, property_type: type) -> Dict[str, Any]:
        """
        Sérialise une propriété de type flag Qt en catégorisant ses valeurs.

        Les flags Qt sont des champs de bits où certaines valeurs sont mutuellement
        exclusives au sein d'un groupe (ex: les différentes politiques d'alignement
        horizontal) et d'autres sont librement combinables (ex: les coins d'un
        layout).

        L'algorithme de catégorisation exploite les membres dont le nom contient
        'Mask' : chaque masque délimite un groupe exclusif en définissant les
        bits qu'il couvre. Pour chaque valeur candidate :

        - Si `valeur | masque == masque` (tous les bits de la valeur sont couverts
          par le masque), la valeur appartient au groupe exclusif de ce masque.
        - Si `valeur & masque != 0` sans satisfaire la condition précédente, la
          valeur chevauche partiellement le masque — elle est ignorée car elle
          représente probablement le masque lui-même ou une combinaison invalide.
        - Si aucun masque ne couvre la valeur, elle est non-exclusive et peut
          être combinée librement avec d'autres flags via `|`.

        Args:
            q_meta_property (QMetaProperty): L'objet QMetaProperty à traiter.
            property_type (type): Le type de flag Qt de la propriété.

        Returns:
            Dict[str, Any]: Un dictionnaire avec les clés 'type', 'options'
                (contenant 'exclusive' et 'non_exclusive'), 'namespace' et
                optionnellement 'default' (si non abstrait).
        """
        type_name = "flag"

        options: Dict[str, Any] = {"exclusive": {}, "non_exclusive": []}
        mask: Dict[str, int] = {}
        value_to_filter: Dict[str, int] = {}

        namespace = self.__extract_namespace(q_meta_property, property_type)

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
            default: Dict[str, Any] = {"exclusive": {}, "non_exclusive": []}

            flag = q_meta_property.read(self._obj)
            values = flag.name.split(sep="|")

            for value in values:
                if value in options["non_exclusive"]:
                    default["non_exclusive"].append(value)
                else:
                    for category, collection in options["exclusive"].items():
                        if value in collection:
                            default["exclusive"][category] = value

            return {"type": type_name, "default": default, "options": options, "namespace": namespace}
        else:
            return {"type": type_name, "options": options, "namespace": namespace}

    def __extract_namespace(self, q_meta_property: QMetaProperty, property_type: type) -> List[str]:
        """
        Construit le namespace d'accès Python pour une propriété énumération ou flag.

        Utilise `QMetaProperty.enumerator()` pour récupérer le scope Qt original
        (ex: 'Qt', 'QFrame') et le nom de l'énumération (ex: 'AlignmentFlag',
        'Shape'). Ces informations ne sont pas accessibles via le type Python
        seul car PySide6 aplatit la hiérarchie de namespaces C++ lors du binding.

        Le namespace produit permet de reconstruire l'expression Python exacte
        dans le code généré (ex: `['PySide6.QtCore', 'Qt', 'AlignmentFlag']`
        → `Qt.AlignmentFlag.AlignLeft`).

        Args:
            q_meta_property (QMetaProperty): L'objet QMetaProperty contenant
                les informations sur l'énumérateur.
            property_type (type): Le type d'énumération ou de flag Qt.

        Returns:
            List[str]: La liste des composants du namespace, débutant par le
                module Python, suivi du scope si différent du nom, puis du nom
                de l'énumération.
        """
        namespace = []

        module = property_type.__module__
        scope = q_meta_property.enumerator().scope()
        name = q_meta_property.enumerator().enum_name()

        namespace.append(module)
        if scope != name:
            namespace.append(scope)
        namespace.append(name)

        return namespace

    def __extract_methods(self, recursive: bool = True) -> Dict[str, Any]:
        """
        Extrait les signaux et slots supportés via QMetaObject.

        Contrairement à `inspect` qui expose les signaux comme des descripteurs
        opaques sans information sur leurs paramètres, `QMetaObject` retourne
        le type de méthode (`Signal`, `Slot`, `Method`), les noms et types C++
        précis de chaque paramètre via `parameter_names()` et `parameter_types()`.
        Cette précision est nécessaire pour générer du code de connexion valide.

        Lorsque `recursive=False`, l'itération démarre à `method_offset()` pour
        n'inclure que les méthodes introduites par la classe courante.

        Args:
            recursive (bool): Si True, inclut les méthodes héritées (offset 0).
                Si False, commence à l'offset de la classe courante.

        Returns:
            Dict[str, Any]: Un dictionnaire avec les clés 'signal' et 'slot',
                chacune contenant les méthodes supportées indexées par nom.
        """
        offset = 0 if recursive else self._meta.method_offset()
        methods: Dict[str, Any] = {"signal": {}, "slot": {}}
        for idx in range(offset, self._meta.method_count()):
            meta_method = self._meta.method(idx)
            method_name = meta_method.name().data().decode()
            method_type = meta_method.method_type()

            parameters, parameters_valid = self.__extract_params(meta_method)

            if not parameters_valid:
                continue

            if method_type == QMetaMethod.MethodType.Signal:
                method_type = "signal"
            elif method_type == QMetaMethod.MethodType.Slot:
                method_type = "slot"
                method_name = mds.to_snake_case(method_name)
            else:
                continue

            if method_name not in methods[method_type]:
                methods[method_type][method_name] = {}
                methods[method_type][method_name]["name"] = method_name
                methods[method_type][method_name]["parameter"] = parameters

        return methods

    def __extract_params(self, meta_method: QMetaMethod) -> Tuple[List[Dict[str, Any]], bool]:
        """
        Extrait et valide les paramètres d'une méthode Qt.

        Récupère les noms et types C++ des paramètres via `parameter_names()`
        et `parameter_types()` de QMetaMethod — deux informations absentes de
        l'interface Python normale des signaux et slots. Les types C++ bruts
        (ex: `'const QString&'`) sont d'abord nettoyés des modificateurs de
        pointeur/référence, puis résolus via `type_map`. Si un paramètre a un
        type non supporté, la méthode entière est rejetée.

        Args:
            meta_method (QMetaMethod): L'objet QMetaMethod à analyser.

        Returns:
            Tuple[List[Dict[str, Any]], bool]: Un tuple contenant la liste des
                paramètres sérialisés et un booléen indiquant si tous les
                paramètres sont valides (True) ou si un type non supporté a
                été rencontré (False).
        """
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

            parameters.append({"type": param_type, "name": name})
            if module and module != "builtins":
                parameters[-1]["module"] = module

        return (parameters, parameters_valid)

    def __get_type_name(self, type_name: type) -> Union[str, Dict[str, Any]]:
        """
        Convertit un type Python en sa représentation sérialisée pour le frontend.

        Retourne le nom simple pour les types primitifs et les objets Qt, un
        dictionnaire structuré pour les types complexes (afin de décrire leurs
        attributs attendus), ou la chaîne 'enum' pour les types d'énumération.

        Args:
            type_name (type): Le type Python à convertir.

        Returns:
            Union[str, Dict[str, Any]]: Le nom du type sous forme de chaîne,
                ou un dictionnaire structuré pour les types complexes.
        """
        if type_name in self.__config.primitives_types + self.__config.objects_implemented:
            type_name = type_name.__name__
        elif type_name in self.__config.complex_types_implemented:
            generic_name, attributes = self.__config.complex_types_implemented.get(type_name)
            data = {"type": generic_name}
            value = {}
            for attribute, attr_type in attributes.items():
                value[attribute] = {"type": attr_type.__name__} if attr_type not in self.__config.enum_implemented else {"type": "enum"}
            data["value"] = value
            type_name = data
        elif type_name in self.__config.enum_implemented:
            type_name = "enum"

        return type_name
