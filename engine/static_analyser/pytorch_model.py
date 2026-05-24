from typing import Self, List, Any, Tuple

import torch
import torch.nn as nn


class PyTorchModel(nn.Module):
    def __init__(self:Self, vocab_size: int, embed_dim: int, hidden_dim) -> None:
        super().__init__()
        self._device = torch.accelerator.current_accelerator().type if torch.accelerator.is_available() else "cpu"

        print(f"{self.__class__.__name__} initizalizing")
        print(f"Using {self._device} device")

        self._type_embeddings = nn.Embedding(vocab_size, embed_dim)
        self._value_embeddings = nn.Embedding(vocab_size, embed_dim)
        self._gru = nn.GRU(embed_dim * 2, hidden_dim, batch_first=True)
        self._linear = nn.Linear(hidden_dim, 1)
        
    def forward(self, x):
        type_tensor = self._type_embeddings(x[:,:,0])
        value_tensor = self._value_embeddings(x[:,:,1])
        _, hidden = self._gru(torch.cat([type_tensor, value_tensor], 2))
        result = self._linear(torch.squeeze(hidden, 0))
        return torch.sigmoid(result)

   
                