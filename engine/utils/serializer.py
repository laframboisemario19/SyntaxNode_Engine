import re
from typing import Any
import copy


class MetadataSerializer:
    @staticmethod
    def to_snake_case(text:str) -> str:
        ## Pour la regex : https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case 
        return re.sub(r'(?<!^)(?=[A-Z])', '_', text).lower()
    
    @staticmethod
    def clean_cpp_params(text:str) -> str:
        return re.sub(r'[*&]', '', text)
    
    @staticmethod
    def restructure_dict(data: Any) -> dict[str:list[Any]]:
        working_data = copy.deepcopy(data)

        core_list = [MetadataSerializer._process_node(content) for content in working_data.values()]

        return {"core": core_list}

    @classmethod
    def _process_node(cls, node: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(node, dict):
            return node

        if "children" in node and isinstance(node["children"], dict):
            node["children"] = [cls._process_node(c) for c in node["children"].values()]

        if "property" in node and isinstance(node["property"], dict):
            node["property"] = cls._map_to_list(node["property"])

            for prop in node["property"]:
                if "value" in prop and isinstance(prop["value"], dict):
                    prop["value"] = cls._map_to_list(prop["value"])

        if "method" in node and isinstance(node["method"], dict):
            for m_type in ["signal", "slot"]:
                if m_type in node["method"] and isinstance(node["method"][m_type], dict):
                    node["method"][m_type] = cls._map_to_list(node["method"][m_type])

        return node

    @staticmethod
    def _map_to_list(mapping: dict[str, Any]) -> list[dict[str, Any]]:
        result = []
        for key, value in mapping.items():
            if isinstance(value, dict):
                if "name" not in value:
                    value["name"] = key
                result.append(value)
            else:
                result.append({"name": key, "value": value})
        return result