"""
Paquet des utilitaires pour le moteur SyntaxNode.

Ce paquet regroupe les outils transversaux utilisés par les stratégies,
adaptateurs et générateurs du moteur : sérialisation et organisation des
métadonnées, génération de code source et d'archives ZIP.

Classes
-------
MetadataSerializer: Utilitaire de sérialisation et de transformation des métadonnées.
MetadataOrganizer: Utilitaire de restructuration hiérarchique des métadonnées.
CodeGenerator: Utilitaire de génération de code source et d'archives ZIP.
"""

from .serializer import MetadataSerializer
from .organizer import MetadataOrganizer
from .code_generator import CodeGenerator

__all__ = ["MetadataSerializer", "MetadataOrganizer", "CodeGenerator"]
