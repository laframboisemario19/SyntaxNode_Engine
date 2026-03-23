from abc import ABC, abstractmethod

class BaseConfig(ABC):

    @property 
    @abstractmethod
    def objects_implemented(self):
        pass
    
    @property 
    @abstractmethod
    def primitives_types(self):
        pass
    
    @property 
    @abstractmethod
    def complex_types_implemented(self):
        pass
    
    @property 
    @abstractmethod
    def enum_implemented(self):
        pass
    
    @property 
    @abstractmethod
    def flags_implemented(self):
        pass
    
    @property 
    @abstractmethod
    def params_implemented(self):
        pass
    
    @property 
    @abstractmethod
    def type_map(self):
        pass

    @abstractmethod
    def is_param_supported(self, raw_name:str) -> bool:
        pass