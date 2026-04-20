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
            data, data_dict = self._format_partial_data(target_id, data_dict, root_list)
            root_list = self._builder._find_root(data["components"])

        self._builder.build_import(data["components"])

        self._builder.build_class(data, data_dict)
        self._builder.build_main(data_dict)
        self._builder.fix_locations()
        self._builder.print_tree()

        return self._builder.get_ast()
    
    def _format_partial_data(self:Self, target_id, data_dict, root_list) -> dict[str, Any]:
        new_components = []
        new_data_dict = {}

        root_id = root_list[0] if len(root_list) == 1 else self._find_parent()
        root_variables = data_dict[root_id]["variable"]
        root_properties = data_dict[root_id]["properties"]

        # if data_dict[target_id]["category"] == "widget":
        #     layout = self._create_layout(target_id)
        #     target_id = layout["id"]
        #     new_data_dict[target_id] = layout
        #     # new_components.append(layout)
        #     data_dict[target_id] = layout 

        if data_dict[target_id]["category"] == "layout":
            comp = self._add_root_widget(root_variables, root_properties, target_id, "app_widget")
            new_data_dict[comp["id"]] = comp
            new_components.append(comp)
        else:
            data_dict["app_widget"] = data_dict[target_id].copy()
            data_dict["app_widget"]["id"] = "app_widget"
            data_dict["app_widget"]["type"] = "MyApp"
            data_dict["app_widget"]["category"] = "widget"
            data_dict["app_widget"]["inheritance"].append({"type":data_dict[target_id]["type"], "module":data_dict[target_id]["module"]})
            data_dict.pop(target_id)
            data_dict["app_widget"].pop("module")
            target_id = "app_widget"

        self._add_components(target_id, data_dict, new_components, new_data_dict)
        
        new_data = {"components": new_components, "links": []}
        
        return new_data, new_data_dict
    
    # def _create_layout(self:Self, target_id):
    #     variables = []
    #     children = [target_id]
    #     properties = []
    #     inheritance = [{
    #                     "type": "QWidget",
    #                     "module": "PySide6.QtWidgets"
    #                 }]

    #     layout = {"id" : "my_layout",
    #                    "type" : "MyApp",
    #                    "category" : "core",
    #                    "name": "app",
    #                    "variable": variables,
    #                    "inheritance": inheritance,
    #                    "child": children,
    #                    "properties": properties,
    #                    "function" : []
    #                    }
        
    #     return layout
    
    def _find_parent(self:Self):
        raise Exception("pas encore implémenté.")

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