from __future__ import annotations

from typing import Self, List, Any, Tuple, override, Dict
from enum import Enum, auto
from abc import ABC, abstractmethod
from pathlib import Path
import json
import ast

import torch
from torch.utils.data import Dataset, DataLoader
from torch.nn.utils import rnn

from ..ast_utils import ASTFlattener, ASTDirector, BuilderFactory

TRAINING_DATA_PATH = Path(__file__).parent.parent.parent / "ai_data" / "training_data"
DATASETS_PATH = Path(__file__).parent.parent.parent / "ai_data" / "datasets"
LEXICAL_FILE = TRAINING_DATA_PATH / "data.json"

class TrainingSource(Enum):
    BUGS_IN_PY = auto()
    BANDIT = auto()
    SYNTAX_NODE_ERROR = auto()
    SYNTAX_NODE_MALICIOUS = auto()

class BaseDataSet(Dataset, ABC):
    _lexical = {}
    _max_len = 0
    _flattener = ASTFlattener()
    
    def __init__(self:Self, paths:List[Tuple[str, bool]]) -> None:
        if not BaseDataSet._lexical:
            self.load()
        self._paths:List[Tuple[str, bool]] = paths
        self._build_lexical()

    def __len__(self:Self) -> int:
        return len(self._paths)

    def __getitem__(self:Self, index:int) -> Tuple[torch.Tensor, torch.Tensor]:
        path, expected_value = self._paths[index]
        flatten_tree = self._transform_data(path)
        return self._data_into_tensor(flatten_tree, expected_value)

    def reset(self:Self) -> None:
        BaseDataSet._lexical = {}
        BaseDataSet._max_len = 0

    def save(self:Self) -> None:
        with open(LEXICAL_FILE, "w", encoding="utf-8") as f:
            content = {"lexical":self._lexical, "max_len":BaseDataSet._max_len}
            json.dump(content, f)

    def load(self:Self) -> None:
        try:
            with open(LEXICAL_FILE, "r", encoding="utf-8") as f:
                content = json.load(f)
                BaseDataSet._lexical = content.get("lexical", {})
                BaseDataSet._max_len = content.get("max_len", 0)
        except FileNotFoundError as e:
            BaseDataSet._lexical = {}
            BaseDataSet._max_len = 0

        if not BaseDataSet._lexical:
            BaseDataSet._lexical = {"PAD": 0, "Unknown": 1, "USER_str": 2, "USER_int":3, "USER_float":4, "USER_bool":5, "USER_none":6, "No_value":7}

    def _build_lexical(self:Self) -> None:
        for path, _ in self._paths:
            flatten_tree = self._transform_data(path)
            BaseDataSet._max_len = max(BaseDataSet._max_len, len(flatten_tree))
            for node in flatten_tree:
                word, _, _, _ = node
                if word not in BaseDataSet._lexical:
                    BaseDataSet._lexical[word] = len(BaseDataSet._lexical)
        self.save()

    def _data_into_tensor(self:Self, flatten_tree:Tuple[List[List[Any]]], expected_value:bool) -> Tuple[torch.Tensor, torch.Tensor]:
        user_input = {None: "USER_none", "":"No_value", "str":"USER_str", "int":"USER_int", "float":"USER_float","bool":"USER_bool"}
        main_list = []
        for node in flatten_tree:
            word, _, _, value = node
            word, value = BaseDataSet._lexical.get(word, 1), BaseDataSet._lexical.get(value, value)

            if value not in BaseDataSet._lexical:
                value = user_input.get(value, user_input.get(value.__class__.__name__, "Unknown"))
                value = BaseDataSet._lexical[value]

            main_list.append([word, value])
        data_tensor = torch.tensor([main_list])
        value_tensor = torch.tensor(expected_value)

        return data_tensor, value_tensor
    
    @abstractmethod
    def _transform_data(self:Self, path:str) -> Tuple[List[List[Any]]]:
        with open(path, encoding="utf-8") as file:
            data = json.load(file)
        

    @staticmethod
    def collate_fn(batch:List[Tuple[torch.Tensor, torch.Tensor]]) -> Tuple[torch.Tensor, torch.Tensor]:
        x = rnn.pad_sequence([data[0] for data in batch], batch_first=True)
        y = torch.stack([data[1] for data in batch])

        return x, y 
    
class BugsInPyDataset(BaseDataSet):
    def __init__(self:Self) -> None:
        super().__init__()

class BanditDataset(BaseDataSet):
    def __init__(self:Self, paths:List[Tuple[str, bool]]) -> None:
        super().__init__(paths)

    @override
    def _transform_data(self:Self, path:str) -> Tuple[List[List[Any]]]:
        with open(path) as f:
            tree = ast.parse(f.read())
        return BaseDataSet._flattener.flatten(tree)

class SyntaxNodeDataset(BaseDataSet):
    def __init__(self:Self, library, metadata: Dict[str, Any], paths:List[Tuple[str, bool]]) -> None:
        super().__init__(paths)
        self._metadata = metadata
        self._director = ASTDirector(BuilderFactory.get_builder(library))

    @override
    def _transform_data(self:Self, path:str) -> Tuple[List[List[Any]]]:
        with open(path, encoding="utf-8") as f:
            content = json.load(f)
        tree = self._director.make(content, self._metadata)
        return BaseDataSet._flattener.flatten(tree)
    
class DatasetFactory():
    _sources = {
        TrainingSource.BUGS_IN_PY : BugsInPyDataset,
        TrainingSource.BANDIT : BanditDataset,
        TrainingSource.SYNTAX_NODE_ERROR : SyntaxNodeDataset,
        TrainingSource.SYNTAX_NODE_MALICIOUS : SyntaxNodeDataset
    }

    @staticmethod
    def create(training_source:TrainingSource, library:str | None = None, metadata:Dict[str, Any] | None = None) -> BaseDataSet:
        paths = DatasetFactory._find_paths(training_source)
        if library is None and metadata is None:
            return DatasetFactory._sources[training_source](paths)
        else:
            return DatasetFactory._sources[training_source](paths, library, metadata)
        
    @staticmethod
    def _find_paths(training_source:TrainingSource):
        path_list = []
        folder = training_source.name.lower()
        clean_path = DATASETS_PATH / folder / "clean"
        unclean_path = DATASETS_PATH / folder / "unclean"
        for p in clean_path.iterdir():
            path_list.append((str(p), True))
        for p in unclean_path.iterdir():
            path_list.append((str(p), False))  
        return path_list

