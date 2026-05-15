from typing import Self, List, Any, Tuple

import torch

class PyTorchModel():
    def __init__(self:Self, data:Tuple[List[List[Any]]], import_list:List[str]) -> None:
        self._lexical = {"Unknown": 0, "USER_str": 1, "USER_int":2, "USER_float":3, "USER_bool":4, "USER_none":5, "No_value":6}
        self._device = torch.accelerator.current_accelerator().type if torch.accelerator.is_available() else "cpu"
        self.values = self.transform_data(data)

        for import_from in import_list:
            if import_from not in self._lexical:
                self._lexical[import_from] = len(self._lexical)

        print(f"{self.__class__.__name__} initizalizing")
        print(f"Using {self._device} device")

    def reset(self:Self) -> None:
        self._lexical = {"Unknown": 0, "USER_str": 1, "USER_int":2, "USER_float":3, "USER_bool":4, "USER_none":5, "No_value":6}
        self.values = None

    def transform_data(self:Self, data:Tuple[List[List[Any]]]) -> List[torch.Tensor]:
        tensor_list = []
        user_input = {None: "USER_none", "":"No_value", "str":"USER_str", "int":"USER_int", "float":"USER_float","bool":"USER_bool"}
        for d in data:
            main_list = []
            for node in d:
                word, parent, _, value = node

                if word not in self._lexical:
                    self._lexical[word] = len(self._lexical)

                word, value = self._lexical.get(word, "Unknown"), self._lexical.get(value, value)

                if value not in self._lexical:
                    value = user_input.get(value, user_input.get(value.__class__.__name__, None))
                    value = self._lexical[value]

                main_list.append([word, parent, value])
                main_tensor = torch.tensor([main_list])
            tensor_list.append(main_tensor)

        return tensor_list