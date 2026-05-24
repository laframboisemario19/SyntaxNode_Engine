from typing import Self, Any, List, Dict, Tuple
from pathlib import Path

from .base import LanguageStrategy, ImageGeneratorStrategy
from ..ast_utils import BuilderFactory, ASTDirector, ASTFlattener
from ..generator import CodeGenerator
from ..static_analyser import PyTorchModel
from ..visitors import ImportFromExtractor
from ..static_analyser import DatasetFactory, TrainingSource, BaseDataSet

SN_ERROR_MODEL_PATH = Path(__file__).parent.parent.parent / "ai_data" / "model" / "sn_error.pt"
BANDIT_MODEL_PATH = Path(__file__).parent.parent.parent / "ai_data" / "model" / "bandit.pt"

class PythonStrategy(LanguageStrategy):
    def __init__(self, config=None):
        self._name = "python"
        self._image_generator: ImageGeneratorStrategy = None
        self._available_lib = []
        self._directors: dict[str, ASTDirector] = {}
        self._flattener = ASTFlattener()
        self._sn_error_pytorch_model = None
        self._bandit_pytorch_model = None

    @property
    def name(self):
        return self._name
    
    @property
    def available_lib(self):
        return self._available_lib
        
    @property
    def image_generator(self: Self) -> str:
        return self._image_generator.name

    def get_code_files(self, library, data, metadata):
        if library not in self._directors:
            self._directors[library] = ASTDirector(BuilderFactory.get_builder(library))

        ast = self._directors[library].make(data, metadata)
        code = CodeGenerator.generate_code(ast)

        file = CodeGenerator.generate_file("main_application.py", code)
        zip_file = CodeGenerator.generate_zip_files((file,))

        return zip_file
    
    def generate_bitmap(self: Self, library:str, image_generator:ImageGeneratorStrategy, data: dict[Any, Any], metadata: dict[Any, Any], target_id:str):
        if image_generator.name != library:
            raise ValueError("image_generator n'est pas compatible avec la library spécifié.")
        
        if library not in self._directors:
            self._directors[library] = ASTDirector(BuilderFactory.get_builder(library))
            
        self._image_generator = image_generator
        
        tree = self._directors[library].make(data, metadata, target_id)

        return self._image_generator.generate_preview(tree)
    
    def validate_ast(self:Self, library, data, metadata) -> bool:
        if library not in self._directors:
            self._directors[library] = ASTDirector(BuilderFactory.get_builder(library))

        ast = self._directors[library].make(data, metadata)

        return True
    
    def train_ai(self:Self, library:str, metadata) -> None:
        if library not in self._directors:
            self._directors[library] = ASTDirector(BuilderFactory.get_builder(library))

        import torch
        from torch.utils.data import DataLoader
        
        BaseDataSet.load()

        if not SN_ERROR_MODEL_PATH.exists():
            self._sn_error_pytorch_model = PyTorchModel(len(BaseDataSet._lexical), 32, 64)
            sn_dataset = DatasetFactory.create(TrainingSource.SYNTAX_NODE_ERROR, library, metadata)
            sn_dataloader = DataLoader(sn_dataset, batch_size=32, shuffle=True)
            PythonStrategy._train(self._sn_error_pytorch_model, sn_dataloader, 50)
            torch.save({"state_dict": self._sn_error_pytorch_model.state_dict(), "vocab_size": len(BaseDataSet._lexical)}, SN_ERROR_MODEL_PATH)
        else:
            data = torch.load(SN_ERROR_MODEL_PATH)
            self._sn_error_pytorch_model = PyTorchModel(data["vocab_size"], 32, 64)
            self._sn_error_pytorch_model.load_state_dict(data["state_dict"])

        if not BANDIT_MODEL_PATH.exists():
            self._bandit_pytorch_model = PyTorchModel(len(BaseDataSet._lexical), 32, 64)
            bandit_dataset = DatasetFactory.create(TrainingSource.BANDIT)
            bandit_dataloader = DataLoader(bandit_dataset, batch_size=32, shuffle=True)
            self._train(self._bandit_pytorch_model, bandit_dataloader, 50)
            torch.save({"state_dict": self._bandit_pytorch_model.state_dict(), "vocab_size": len(BaseDataSet._lexical)}, BANDIT_MODEL_PATH)
        else:
            data = torch.load(BANDIT_MODEL_PATH)
            self._bandit_pytorch_model = PyTorchModel(data["vocab_size"], 32, 64)
            self._bandit_pytorch_model.load_state_dict(data["state_dict"])

    @staticmethod
    def _train(model, dataloader, epochs):
        from torch.optim.adam import Adam
        from torch import squeeze
        import torch.nn as nn

        loss = nn.BCELoss()
        optimizer = Adam(model.parameters(), 0.001)

        for epoch in range(epochs):
            loss_accum = 0
            nb_batch = 0
            for batch, labels in dataloader:
                optimizer.zero_grad()
                predictions = model(batch)
                output = loss(squeeze(predictions, 1), labels)
                output.backward()
                optimizer.step()
                loss_accum += output.item()
                nb_batch += 1
            print(f"Moyenne de loss : {loss_accum / nb_batch}")

    def predict(self, library, data, metadata):
        if library not in self._directors:
            self._directors[library] = ASTDirector(BuilderFactory.get_builder(library))

        if self._sn_error_pytorch_model is None or self._bandit_pytorch_model is None:
            self.train_ai(library, metadata)

        from torch import no_grad, unsqueeze
        with no_grad():
            tree = self._directors[library].make(data, metadata)
            flatten_ast = self._flattener.flatten(tree)

            x = unsqueeze(BaseDataSet._data_into_tensor(flatten_ast, False)[0], 0)
            
            result = max(self._sn_error_pytorch_model(x).item(), self._bandit_pytorch_model(x).item())
        
        return result