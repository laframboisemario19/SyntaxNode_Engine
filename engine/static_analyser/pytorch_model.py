"""
Modèle PyTorch pour l'analyse statique du code SyntaxNode.

Ce module fournit la classe `PyTorchModel`, un réseau de neurones récurrent
(GRU) destiné à classifier des arbres syntaxiques aplatis comme sûrs ou
non sûrs. Le modèle est utilisé par `PythonStrategy` pour détecter les
erreurs structurelles et le code potentiellement malveillant.

Classes
-------
PyTorchModel: Réseau de neurones GRU pour la classification d'AST aplatis.
"""

from typing import Self, List, Any, Tuple

import torch
import torch.nn as nn


class PyTorchModel(nn.Module):
    """
    Réseau de neurones GRU pour la classification d'AST aplatis.

    Encode les nœuds d'un AST aplati via deux couches d'embeddings (type et
    valeur), les traite avec un GRU et produit une probabilité de classification
    binaire via une couche linéaire et une activation sigmoïde.

    Attributes:
        _device (str): Le dispositif de calcul utilisé ('cuda', 'mps' ou 'cpu').
        _type_embeddings (nn.Embedding): La couche d'embeddings pour le type
            de chaque nœud AST.
        _value_embeddings (nn.Embedding): La couche d'embeddings pour la valeur
            de chaque nœud AST.
        _gru (nn.GRU): La couche GRU traitant la séquence de nœuds encodés.
        _linear (nn.Linear): La couche linéaire produisant le score de classification.
    """

    def __init__(self: Self, vocab_size: int, embed_dim: int, hidden_dim: int) -> None:
        """
        Initialise le modèle avec les dimensions spécifiées.

        Args:
            vocab_size (int): La taille du vocabulaire (nombre de tokens uniques
                dans le lexique de l'AST).
            embed_dim (int): La dimension des vecteurs d'embeddings pour les
                types et valeurs de nœuds.
            hidden_dim (int): La dimension de l'état caché du GRU.
        """
        super().__init__()
        self._device = torch.accelerator.current_accelerator().type if torch.accelerator.is_available() else "cpu"

        print(f"{self.__class__.__name__} initizalizing")
        print(f"Using {self._device} device")

        self._type_embeddings = nn.Embedding(vocab_size, embed_dim)
        self._value_embeddings = nn.Embedding(vocab_size, embed_dim)
        self._gru = nn.GRU(embed_dim * 2, hidden_dim, batch_first=True)
        self._linear = nn.Linear(hidden_dim, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Effectue la passe avant du modèle sur un batch de séquences de nœuds.

        Encode les types et valeurs des nœuds, les concatène, les traite via
        le GRU et retourne la probabilité de classification via une sigmoïde.

        Args:
            x (torch.Tensor): Un tenseur de forme `(batch, seq_len, 2)` où
                `x[:,:,0]` contient les indices de types et `x[:,:,1]` les
                indices de valeurs.

        Returns:
            torch.Tensor: Un tenseur de forme `(batch, 1)` contenant la
                probabilité que chaque séquence soit classifiée comme non sûre.
        """
        type_tensor = self._type_embeddings(x[:, :, 0])
        value_tensor = self._value_embeddings(x[:, :, 1])
        _, hidden = self._gru(torch.cat([type_tensor, value_tensor], 2))
        result = self._linear(torch.squeeze(hidden, 0))
        return torch.sigmoid(result)
