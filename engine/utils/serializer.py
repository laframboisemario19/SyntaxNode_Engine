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
    def sanitize_properties(cls, data: dict[str, Any], metadata: dict[str, Any]):
        for component in data:
            comp_type = component["type"] if component.get("module") else component["inheritance"][0]["type"]
            meta_properties = metadata[comp_type]["property"]

            cleaned_properties = []

            for prop in component["properties"]:
                prop_name = prop["name"]
                prop_value = prop["value"]
                keep_property = True

                if isinstance(prop_value, str):
                    if meta_properties[prop_name]["default"] == prop_value:
                        keep_property = False

                elif isinstance(prop_value, list):
                    for param in prop_value:
                        param_name = param["name"]
                        param_value = param["value"]
                        if meta_properties[prop_name]["value"][param_name]["default"] == param_value:
                           keep_property = False
                           break

                if keep_property:
                    cleaned_properties.append(prop)
            
            component["property"] = cleaned_properties

    @classmethod
    def _process_node(cls, node: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(node, dict):
            return node

        if "children" in node and isinstance(node["children"], dict):
            node["children"] = [cls._process_node(c) for c in node["children"].values()]

        if "property" in node and isinstance(node["property"], dict):
            node["property"] = cls.map_to_list(node["property"])

            for prop in node["property"]:
                if "value" in prop and isinstance(prop["value"], dict):
                    prop["value"] = cls.map_to_list(prop["value"])

        if "method" in node and isinstance(node["method"], dict):
            for m_type in ["signal", "slot"]:
                if m_type in node["method"] and isinstance(node["method"][m_type], dict):
                    node["method"][m_type] = cls.map_to_list(node["method"][m_type])

        return node

    @staticmethod
    def map_to_list(mapping: dict[str, Any]) -> list[dict[str, Any]]:
        result = []
        for key, value in mapping.items():
            if isinstance(value, dict):
                if "name" not in value:
                    value["name"] = key
                result.append(value)
            else:
                result.append({"name": key, "value": value})
        return result
    
    @staticmethod
    def list_to_map(listing: list[dict[str, Any]]):
        result = {}

        def _recursive(node, current_parent_id = None):
            if isinstance(node, dict):
                node_id = node.get("id")

                if node_id:
                    result[node_id] = node

                    if current_parent_id:
                        node["parent_id"] = current_parent_id
                
                    next_parent = node_id
                
                else:
                    next_parent = current_parent_id

                for value in node.values():
                    _recursive(value, next_parent)

            elif isinstance(node, list):
                for item in node:
                    _recursive(item, current_parent_id)
            
        _recursive(listing)

        return result