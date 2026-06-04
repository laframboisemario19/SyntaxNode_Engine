"""
Paquet des adaptateurs de métadonnées pour le moteur SyntaxNode.

Ce paquet fournit les adaptateurs responsables de l'extraction et de la
sérialisation des métadonnées des composants graphiques via les systèmes
d'introspection spécifiques à chaque bibliothèque (ex: QMetaObject pour Qt).

Classes
-------
MetadataAdapter: Contrat abstrait pour l'extraction des métadonnées d'un composant.
QtMetadataAdapter: Adaptateur concret d'extraction des métadonnées Qt/PySide6.
"""

from .base import MetadataAdapter
from .qt_adapter import QtMetadataAdapter

__all__ = ["MetadataAdapter", "QtMetadataAdapter"]
