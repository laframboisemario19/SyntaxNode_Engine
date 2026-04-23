
from typing import Any, Dict
import copy

class MetadataOrganizer:
    
    @staticmethod
    def organize_dict(dict_to_organize: Dict[Any, Any], key_word:str) -> Dict[Any, Any]:
        working_data = copy.deepcopy(dict_to_organize)
        root_objects = []

        for data in working_data.values():
            data["children"] = {}

        for name, data in working_data.items():
            parent_name = data.get(key_word)

            if parent_name and parent_name in working_data:
                working_data[parent_name]["children"][name] = data
            else :
                root_objects.append(name)

        for data in working_data.values():
            if key_word in data:
                del data[key_word]

        return {name : working_data[name] for name in root_objects}