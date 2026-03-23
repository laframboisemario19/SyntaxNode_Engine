
from typing import Any

class MetadataOrganizer:
    
    @staticmethod
    def organize_dict(dict_to_organize: dict[Any, Any], key_word) -> dict[Any, Any]:
        root_objects = []

        for data in dict_to_organize.values():
            data["children"] = {}

        for name, data in dict_to_organize.items():
            parent_name = data.get(key_word)

            if parent_name and parent_name in dict_to_organize:
                dict_to_organize[parent_name]["children"][name] = data
            else :
                root_objects.append(name)

        for data in dict_to_organize.values():
            if key_word in data:
                del data[key_word]

        return {name : dict_to_organize[name] for name in root_objects}