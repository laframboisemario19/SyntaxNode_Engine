import ast
from .ast_builder import ASTBuilder
from typing import Any


class QtASTBuilder(ASTBuilder):
    def __init__(self):
        self._tree = None
        self._current_root = {}
        self._first_root_id = None
        self._root_variable = []

        self._primitive_type = ["int", "str", "bool", "float"]
        self._structure_type = {"list" : ast.List, "tuple": ast.Tuple, "dict": ast.Dict, "set": ast.Set}
        
    @property
    def tree(self):
        return self._tree

    def reset(self):
        self._tree = None
        self._current_root = {}
        self._first_root_id = None
        self._root_variable = []

    def create_tree(self):
        self._tree = ast.Module(body=[], type_ignores=[])

    def get_ast(self):
        tree = self._tree
        self.reset()
        return tree
    
    def build_import(self, data):
        import_buffers = {"system": set(), "qt":{}, "feature":{}, "local":{}}
        self._add_static_import(import_buffers)

        self._add_dynamic_import(data, import_buffers)

        self._build_import_nodes(import_buffers)

    def build_class(self, data, data_dict):
        component = data["components"]
        root_list = self._find_root(component)
        self._build_class_node(root_list, data_dict)
        for node_id, node in self._current_root.items():
            if not self._first_root_id:
                self._first_root_id = node_id
            self._build_init_node(node_id, node, data, data_dict)
            self._build_function(node.body, data_dict[node_id]["function"])

    def build_main(self, data_dict):
        # Création de la fonction main
        args = ast.arguments(posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[])
        main_node = ast.FunctionDef(name="main", args=args, body=[], decorator_list=[], type_params=[])
        self._tree.body.append(main_node)

        # Définition de la fonction main
        body = main_node.body

        ## app = QApplication(sys.argv)
        call_func = ast.Name(id="QApplication", ctx=ast.Load())
        call_args = [ast.Attribute(value=ast.Name(id="sys", ctx=ast.Load()), attr='argv', ctx=ast.Load())]

        assign_targets = [ast.Name(id="app", ctx=ast.Store())]
        assign_value = ast.Call(func=call_func, args=call_args, keywords=[])

        body.append(ast.Assign(targets=assign_targets, value= assign_value))

        ## w = MyApp()
        assign_targets = [ast.Name(id="w", ctx=ast.Store())]
        assign_value = ast.Call(func=ast.Name(id=data_dict[self._first_root_id]["type"], ctx=ast.Load()), args=[], keywords=[])
        body.append(ast.Assign(targets=assign_targets, value=assign_value))

        ## w.show()
        expr_value = ast.Call(func=ast.Attribute(value=ast.Name(id="w", ctx=ast.Load()), attr="show", ctx=ast.Load()), args=[], keywords=[])
        body.append(ast.Expr(value=expr_value, args=[], keywords=[]))

        ## sys.exit(app.exec())

        call_func = ast.Attribute(value=ast.Name(id="sys", ctx=ast.Load()), attr="exit", ctx=ast.Load())
        call_args = [ast.Call(func=ast.Attribute(value=ast.Name(id="app", ctx=ast.Load()), attr="exec", ctx=ast.Load()), args=[], keywords=[])]
        body.append(ast.Expr(value=ast.Call(func=call_func, args= call_args, keywords=[])))

        # Section if __name__ == "__main__"
        if_test = ast.Compare(left=ast.Name(id="__name__", ctx=ast.Load()), ops=[ast.Eq()], comparators=[ast.Constant(value="__main__")])
        if_body = [ast.Expr(value=ast.Call(func=ast.Name(id="main", ctx=ast.Load()), args=[], keywords=[]))]

        if_main_node = ast.If(test=if_test, body=if_body, orelse=[])
        self._tree.body.append(if_main_node)
                                                
    def _build_class_node(self, root_list, data_dict):
        for root_id in root_list:
            root = data_dict[root_id]
            root_node = ast.ClassDef(name = root["type"], 
                                                bases = [ast.Name(id = i["type"], ctx=ast.Load()) for i in root["inheritance"]],
                                                keywords=[],
                                                body=[],
                                                decorator_list=[],
                                                type_params=[])
            self._tree.body.append(root_node)
            self._current_root[root_id] = root_node
    
    def _build_init_node(self, class_node_id, class_node, data, data_dict):
        init_node = ast.FunctionDef(name = "__init__",
                                    args = ast.arguments(posonlyargs=[],
                                                        args=[
                                                            ast.arg(arg='self'),
                                                            ast.arg(arg='parent')
                                                            ],
                                                        kwonlyargs=[],
                                                        kw_defaults=[],
                                                        defaults=[ast.Constant(value=None)]),
                                    body = [],
                                    decorator_list=[],
                                    type_params=[])
        class_node.body.append(init_node)

        self._build_init_body(class_node_id, init_node.body, data, data_dict)
        
    def _build_init_body(self, class_node_id, body, data, data_dict):  
        body.append(self._build_super_init_node())
        self._build_init_variable(class_node_id, body, data_dict)
        self._build_properties(body, data_dict[class_node_id]["properties"], ast.Name(id="self", ctx=ast.Load()), data_dict)
        self._build_hierarchy(class_node_id, data_dict[class_node_id], body, data, data_dict)
        self._build_links(class_node_id, body, data, data_dict)
        pass

    def _build_super_init_node(self) -> ast.Expr:
        super_node = ast.Name(id="super", ctx=ast.Load())
        parent_node = ast.Name(id="parent", ctx=ast.Load())
        super_call = ast.Call(func=super_node, args=[], keywords=[])

        init_func = ast.Attribute(value=super_call, attr="__init__", ctx=ast.Load())
        init_call = ast.Call(func = init_func, args=[parent_node], keywords=[])
        
        return ast.Expr(value = init_call)

    def _build_init_variable(self, class_node_id, body, data_dict):
        root_data = data_dict[class_node_id]
        components_nodes = []
        variables_nodes = []

        # scope = ["", "_"]
        for var in root_data["variable"]:
            if var["value"]["type"] == "id":
                self._root_variable.append(var["value"]["value"])
            target_value = ast.Name(id='self', ctx=ast.Load())
            target_attr = var["name"]
            target_ctx = ast.Store()
            var_target = [ast.Attribute(value=target_value, attr=target_attr, ctx=target_ctx)]

            var_value = None
            var_data = var["value"]

            var_value = self._process_variable_value(var_data, data_dict)

            if not var_value:
                continue

            assign_node = ast.Assign(targets=var_target, value=var_value)


            if var_data["type"] == "id":
                components_nodes.append([assign_node, var_data])
            else:
                variables_nodes.append([assign_node, var_data])
                
        for node, var_data in variables_nodes:
            body.append(node)
        for node, var_data in components_nodes:
            body.append(node)
            self._build_properties(body, 
                                data_dict[var_data["value"]]["properties"], 
                                ast.Attribute(value=ast.Name(id="self", ctx=ast.Load()), attr=data_dict[var_data["value"]]["name"], ctx=ast.Load()), 
                                data_dict)

    def _process_variable_value(self, var, data_dict):
        if var["type"] in self._primitive_type:
            return ast.Constant(value = var["value"])
        
        elif var["type"] == "id" and var["value"] in data_dict:
            call_func = ast.Name(id=data_dict[var["value"]]["type"], ctx=ast.Load())
            return ast.Call(func=call_func, args=[], keywords=[])

        elif var["type"] in self._structure_type:
            kwargs = {}

            if var["type"] == "dict":
                kwargs["keys"] = [ast.Constant(value=k) for k in var.get("key", [])]
                kwargs["values"] = [self._process_variable_value(v, data_dict) for v in var.get("value", [])]
            else:
                kwargs["elts"] = [self._process_variable_value(v, data_dict) for v in var.get("value", [])]

            if var["type"] in ["list", "tuple"]:
                kwargs["ctx"] = ast.Load()

            return self._structure_type[var["type"]](**kwargs)

        elif var["type"] == "enum":
            return self._build_property_value(var["namespace"][2], var["namespace"][1], var["value"])
        
        elif var["type"] == "flag":
            return self._build_flag_value(var["value"], var["namespace"])

        elif var["type"] == "expression":
            return ast.parse(var["value"]).body[0].value
        
    def _add_static_import(self, import_buffers):
        import_buffers["system"].add("sys")
        import_buffers["qt"]["PySide6.QtWidgets"] = set(("QApplication",))
        import_buffers["feature"]["__feature__"] = set(("snake_case", "true_property"))

    def _add_dynamic_import(self, components, import_buffers):
        data = self._find_data(("module", "inheritance", "properties"), components)
        self._process_system_data(data, import_buffers["system"])
        self._process_qt_data(data, import_buffers["qt"])
        self._process_local_data(data, import_buffers["local"])

    def _find_data(self, keys: tuple[str], data_list: dict[str, list | str]):
        items = []

        for item in data_list:
            for key in keys:
                if item.get(key):
                    if isinstance(item.get(key), str):
                        items.append(item)
                    elif isinstance(item.get(key), list):
                        items.extend(item[key])

        return items
    
    def _process_qt_data(self, extracted_data, target_buffer):
        for item in extracted_data:
            target_key = None
            target_value = None

            if item.get("category") == "custom":
                return None
            if item.get("module"):
                target_key = item["module"]
                target_value = item["type"]
            elif item.get("namespace"):
                target_key = item["namespace"][0]
                target_value = item["namespace"][1]

            if target_key and target_value:
                target_buffer.setdefault(target_key, set()).add(target_value)

    def _process_system_data(self, json_data, import_data):
        ...

    def _process_local_data(self, json_data, import_data):
        ...

    def _build_import_nodes(self, import_buffers):
        for data in import_buffers.values():
            if isinstance(data, set):
                for alias_name in data:
                    self._tree.body.append(ast.Import(names=[ast.alias(name = alias_name)]))
            elif isinstance(data, dict):
                for mod, alias_name in data.items():
                    self._tree.body.append(ast.ImportFrom(module=mod, 
                                                     names=[ast.alias(name=n) for n in alias_name],
                                                     level=0))
            else:
                raise TypeError("format de l'import inconnu.")
            
    def _find_root(self, data):
        child_set = set()
        id_set = set()

        for component in data:
            child_set.update(component["child"])
            id_set.add(component["id"])
        
        return list(id_set.difference(child_set))

    def _build_properties(self, node: list[Any], properties: list[dict[str, Any]], target_name, data_dict):
        for prop in properties:
            assign_targets = ast.Attribute(value=target_name, attr=prop["name"], ctx=ast.Store())
            assign_value = None

            val = prop["value"]

            assign_value = self._process_variable_value(prop, data_dict)

            if assign_value is None:
                func_call = ast.Name(id=prop["type"], ctx=ast.Load())
                args_call = []
                keywords_call = []
                for v in val:
                    keywords_call.append(ast.keyword(arg=v["name"], value=self._process_variable_value(v, data_dict)))
                assign_value = ast.Call(func=func_call, args = args_call, keywords=keywords_call)

            node.append(ast.Assign(targets=[assign_targets], value=assign_value))

    def _build_flag_value(self, flag_value, property_namespace):
        assign_value = None
        left_op = None
        right_op = None
        for v in (flag_value["exclusive"].values() or flag_value["non_exclusive"]):
            left_op = assign_value
            right_op = self._build_property_value(property_namespace[2], property_namespace[1], v)

            if left_op and right_op:  
                assign_value = ast.BinOp(
                        left = left_op,
                        op = ast.BitOr(),
                        right = right_op
                    )
            else: 
                assign_value = right_op
        return assign_value

    def _build_property_value(self, child_name, parent_name, value):
        return ast.Attribute(
                    value = ast.Attribute(
                        value = ast.Name(id=parent_name, ctx=ast.Load()),
                        attr = child_name,
                        ctx = ast.Load()
                    ),
                    attr = value,
                    ctx = ast.Load()
                )
    
    def _build_function(self, body, functions):
        for func in functions:
            if not func.get("is_intern", True):
                arguments = ast.arguments(posonlyargs=[], args=[ast.arg(arg=p) for p in func["params"]], kwonlyargs=[], kw_defaults=[], defaults=[])
                code = "\n".join(func["code"])

                func_body = ast.parse(code).body
                if not func_body:
                    func_body = [ast.Pass()]

                func_node = ast.FunctionDef(name = func["name"],
                                args = arguments,
                                body = func_body,
                                decorator_list = [],
                                type_params = [])
                body.append(func_node)

    def _build_links(self, root_id, body, data, data_dict):
        for link in data["links"]:
            source_id = link["source"]
            target_id = link["target"]
            parent_source_id = data_dict[source_id].get("parent_id")
            parent_target_id = data_dict[target_id].get("parent_id")

            source_name = data_dict[source_id]["name"] if source_id != root_id else "self"
            target_name = data_dict[target_id]["name"] if target_id != root_id else "self"
            parent_source_name = data_dict[parent_source_id]["name"] if parent_source_id and parent_source_id != root_id else "self"
            parent_target_name = data_dict[parent_target_id]["name"] if parent_target_id and parent_target_id != root_id else "self"
            
            if parent_target_name == "self":
                target_base = ast.Name(id="self", ctx=ast.Load())
            else:
                target_base = ast.Attribute(value=ast.Name(id="self", ctx=ast.Load()), attr=parent_target_name, ctx=ast.Load())
            target_attr = ast.Attribute(value=target_base, attr=target_name, ctx=ast.Load())


            if parent_source_name == "self":
                parent_attr = ast.Name(id="self", ctx=ast.Load())
            else:
                parent_attr = ast.Attribute(value=ast.Name(id="self", ctx=ast.Load()), attr=parent_source_name, ctx=ast.Load())
            child_attr = ast.Attribute(value=parent_attr, attr=source_name, ctx=ast.Load())

            connect_attr = ast.Attribute(value=child_attr, attr='connect', ctx=ast.Load())
            call_node = ast.Call(func=connect_attr, args=[target_attr], keywords=[])
            
            body.append(ast.Expr(value=call_node))

    def _build_hierarchy(self, root_id, root_node, body, data, data_dict):
        parent_id = root_id
        parent_node = data_dict[parent_id]
        
        children = parent_node.get("child", [])

        for child in children:
            if child not in self._root_variable:
                child_node = data_dict[child]
                
                assign_target = ast.Name(id=child_node["name"], ctx=ast.Store())
                
                func_call = ast.Name(id=child_node["type"], ctx=ast.Load())
                assign_value = ast.Call(func=func_call, args=[], keywords=[])
                
                body.append(ast.Assign(targets=[assign_target], value=assign_value))

            self._generate_qt_add_method(parent_id, child, body, data_dict)
            self._build_hierarchy(child, root_node, body, data, data_dict)

    def _generate_qt_add_method(self, parent_id, child_id, body, data_dict):
        child_category = data_dict[child_id].get("category", "widget") 
        child_category = data_dict[child_id].get("inheritance", {})[0].get("type", "widget") if child_category == "custom" else child_category
        
        parent_target_name = data_dict[parent_id]["name"]
        child_target_name = data_dict[child_id]["name"]
        
        if parent_id in self._current_root:
            method_name = "set_layout"
            parent_ast = ast.Name(id="self", ctx=ast.Load())
        else:
            parent_category = data_dict[parent_id].get("category", "widget") 
            parent_category = data_dict[parent_id].get("inheritance", {})[0].get("type", "widget") if parent_category == "custom" else parent_category

            if data_dict[parent_id]["category"] == "widget":
                method_name = "set_layout"
            else:
                method_name = "add_widget" if child_category == "widget" else "add_layout"
            if parent_id in self._root_variable:
                parent_ast = ast.Attribute(value=ast.Name(id="self", ctx=ast.Load()), attr=parent_target_name, ctx=ast.Load())
            else:
                parent_ast = ast.Name(id=parent_target_name, ctx=ast.Load())

        if child_id in self._root_variable:
            child_ast = ast.Attribute(value=ast.Name(id="self", ctx=ast.Load()), attr=child_target_name, ctx=ast.Load())
        else:
            child_ast = ast.Name(id=child_target_name, ctx=ast.Load())

        call_node = ast.Expr(
            value=ast.Call(
                func=ast.Attribute(
                    value=parent_ast,  
                    attr=method_name,
                    ctx=ast.Load()
                ),
                args=[child_ast],
                keywords=[]
            )
        )
        body.append(call_node)