import ast
import json

class QtASTBuilder():
    def __init__(self):
        self._tree = None

    def reset(self):
        self._tree = None

    def create_tree(self):
        self._tree = ast.Module(body=[], type_ignores=[])

    def get_ast(self):
        tree = self._tree
        self.reset()
        return tree
    
    def build_import(self, data):
        module = {"PySide6.QtWidgets": set(("QApplication",))}
        project = data[0]
        components = project["components"]

        for c in components:
            if "module" in c:
                if c["module"] not in module:
                    module[c["module"]] = set()
                module[c["module"]].add(c["type"])
            if "inheritance" in c:
                for inheritance in c["inheritance"]:
                    if inheritance["module"] not in module:
                        module[inheritance["module"]] = set()
                    module[inheritance["module"]].add(inheritance["type"])

        self._tree.body.append(ast.Import(names=[ast.alias(name="sys")]))
        for mod, alias_name in module.items():
            self._tree.body.append(ast.ImportFrom(module=mod, 
                                                     names=[ast.alias(name=n) for n in alias_name],
                                                     level=0))
        self._tree.body.append(ast.ImportFrom(module="PySide6.QtCore",
                                                 names=[ast.alias(name="Qt")],
                                                 level=0))
        self._tree.body.append(ast.ImportFrom(module="__feature__",
                                                 names=[ast.alias(name='snake_case'),
                                                        ast.alias(name='true_property')],
                                                        level=0))

    def build_node(self):
        pass

    def print_tree(self):
        print(ast.dump(self._tree, indent=4))


## =================== Tests =======================

def main():
    path = "./data/projet_test.json"
    data = None
    with open(path) as file:
        data = json.load(file)

    path = "./data/all_meta_objects.json"
    metadata = None
    with open(path) as file:
        metadata = json.load(file)


    builder = QtASTBuilder()
    builder.create_tree()
    builder.build_import(data)

    builder.print_tree()

if __name__ == "__main__":
    main()