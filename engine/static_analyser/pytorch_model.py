from typing import Self, List, Any

# import torch

class PyTorchModel():
    def __init__(self:Self) -> None:
        self._lexical = {}
        self.values = None

    def create_tensor(self:Self, data:List[List[Any]]):
        self._update_lexical(data)

    def _update_lexical(self:Self, data:List[List[Any]]):

        for row in data:
            word = row[0]
            if word not in self._lexical:
                self._lexical[word] = len(self._lexical)
        pass