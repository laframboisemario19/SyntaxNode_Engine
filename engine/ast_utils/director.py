from typing import Self, List, Dict, Any

from .ast_builder import ASTBuilder
from ..utils import MetadataSerializer as mds

class ASTDirector():

    def __init__(self, builder:ASTBuilder):
        self._builder = builder
    
    def change_builder(self, builder:ASTBuilder):
        self._builder = builder

    def make(self, data, metadata, target_id = ""):
        data = data[0]
        mds.sanitize_properties(data["components"], metadata)

        self._builder.reset()
        self._builder.create_tree()  

        data_dict = mds.list_to_map(data["components"])

        root_list = self._builder._find_root(data["components"])

        if target_id:
            self._rearrange_data(target_id, data_dict, data["components"], root_list[0])
            self._builder._find_root(data["components"])
            data["links"] = []

        self._builder.build_import(data["components"])

        self._builder.build_class(data, data_dict)
        self._builder.build_main(data_dict)
        self._builder.fix_locations()
        # self._builder.print_tree()

        return self._builder.get_ast()
    
    def _rearrange_data(self:Self, target_id, data_dict, components, root_id) -> None:
        parent_id = self._find_parent(target_id, components)
        parent = data_dict.get(parent_id, None)
        if parent:
            parent_category = parent["category"]

        grand_parent = self._find_parent(parent_id, components)

        target = data_dict[target_id]
        target_category = target.get("category", None)

        root = data_dict[root_id]
        root["type"] = "MyApp"

        if target_category == "layout" and parent_category == "widget":
            self._replace_parent_widget(parent, grand_parent, target, components, data_dict, root)
        elif target_category == "layout" and parent_category == "layout":
            self._add_parent_widget(parent, grand_parent, target, components, data_dict, root)
        elif target_category == "widget":
            self._rearrange_target_widget(target, parent, components, data_dict, root)

        pass

    def _replace_parent_widget(self:Self, parent, grand_parent, target, components, data_dict, root):
        inheritance = []
        w_type = "QWidget"
        if parent == root:
            inheritance = [{"type": "QWidget",
                            "module": "PySide6.QtWidgets"
                            }]
            w_type = "MyApp"
                    
        variable = parent["variable"]
        properties = parent["properties"]
        child = parent["child"]

        widget = {"id" : "my_widget",
                "type" : w_type,
                "category" : "widget",
                "name": "my_widget",
                "variable": variable,
                "inheritance": inheritance,
                "child": child,
                "properties": properties,
                "function" : []
                }
        
        components.append(widget)
        components.remove(parent)
        data_dict["my_widget"] = widget
        data_dict.pop(parent["id"])

        if grand_parent:
            data_dict[grand_parent]["child"].remove(parent["id"])
            data_dict[grand_parent]["child"].append(widget["id"])

        id_in_variable = [var["value"]["value"] for var in root["variable"]]
        if target["id"] not in id_in_variable and parent != root:
            variable = {
                "id": "my_widget",
                "name": "my_widget",
                "value": { "type": "id", "value": "my_widget" },
                "scope": "public",
            }
            root["variable"].append(variable)
    
    def _add_parent_widget(self:Self, parent, target, components, data_dict, root):
        widget = {"id" : "my_widget",
                "type" : "QWidget",
                "category" : "widget",
                "name": "my_widget",
                "variable": [],
                "inheritance": [],
                "child": [target["id"]],
                "properties": [],
                "function" : []
                }
        
        parent["child"].remove(target["id"])
        parent["child"].append(widget["id"])
        components.append(widget)
        data_dict["my_widget"] = widget


        id_in_variable = [var["id"] for var in root["variable"]]
        if target["id"] not in id_in_variable:
            variable = {
                "id": "my_widget",
                "name": "my_widget",
                "value": { "type": "id", "value": "my_widget" },
                "scope": "public",
            }
            root["variable"].append(variable)

    def _rearrange_target_widget(self:Self, target, parent, components, data_dict, root):
        if target["id"] == root["id"]:
            return

        target["name"] = "my_widget"

        for var in root["variable"]:
            if target["id"] == var["value"]["value"]:
                var["name"] = "my_widget"
                return
        variable = {
                "id": "my_widget",
                "name": "my_widget",
                "value": { "type": "id", "value": target["id"] },
                "scope": "public",
            }
        root["variable"].append(variable)
    
    def _find_parent(self:Self, target_id:str, data) -> str:
        for c in data:
            for child_id in c["child"]:
                if child_id == target_id:
                    return c["id"]
        

    def _add_root_widget(self: Self, root_variables, root_properties, child_id:str, widget_id:str):
        variables = root_variables
        children = [child_id]
        properties = root_properties
        inheritance = [{
                        "type": "QWidget",
                        "module": "PySide6.QtWidgets"
                    }]

        application = {"id" : widget_id,
                       "type" : "MyApp",
                       "category" : "core",
                       "name": "app",
                       "variable": variables,
                       "inheritance": inheritance,
                       "child": children,
                       "properties": properties,
                       "function" : []
                       }
        
        return application
    
    def _add_components(self: Self, target_id, data_dict, new_components, new_data_dict):
        comp = data_dict[target_id]
        new_components.append(comp)
        new_data_dict[target_id] = comp

        children = comp.get("child")

        if children:
            for c in children:
                self._add_components(c, data_dict, new_components, new_data_dict)