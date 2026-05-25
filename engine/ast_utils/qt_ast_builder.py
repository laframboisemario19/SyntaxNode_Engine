"""
Implémentation du constructeur d'AST pour la bibliothèque Qt.

Ce module fournit la classe `QtASTBuilder`, qui implémente le contrat
`ASTBuilder` pour générer un arbre syntaxique Python représentant une
interface graphique PySide6 à partir du graphe nodal SyntaxNode.

Classes
-------
QtASTBuilder: Constructeur d'AST concret pour la bibliothèque Qt/PySide6.
"""

import ast
from .ast_builder import ASTBuilder
from ..validators import ASTValidator
from typing import Any, Self, List, Dict, Set, Tuple


class QtASTBuilder(ASTBuilder):
    """
    Constructeur d'AST concret pour la bibliothèque Qt/PySide6.

    Implémente toutes les étapes de construction définies par `ASTBuilder`
    pour générer un arbre syntaxique Python représentant une interface
    graphique PySide6 complète, incluant les imports, les classes, la
    hiérarchie des widgets, les propriétés, les variables, les fonctions
    utilisateur et les connexions de signaux.

    Attributes:
        _tree (ast.Module): L'arbre syntaxique en cours de construction.
        _current_root (dict): Le dictionnaire des nœuds de classe racines
            en cours de construction.
        _first_root_id (str): L'identifiant du premier composant racine,
            utilisé pour la génération du main.
        _root_variable (list): La liste des identifiants de composants
            assignés comme variables de classe.
        _ast_validator (ASTValidator): Le validateur d'AST utilisé pour
            attacher les métadonnées SyntaxNode aux nœuds.
        _primitive_type (list): Les types primitifs Python supportés.
        _structure_type (dict): Les types de structures Python supportés
            et leurs nœuds AST correspondants.
    """
    def __init__(self:Self) -> None:
        """
        Initialise le constructeur avec un état vide et les types supportés.
        """
        self._tree = None
        self._current_root = {}
        self._first_root_id = None
        self._root_variable = []
        self._ast_validator = ASTValidator()

        self._primitive_type = ["int", "str", "bool", "float"]
        self._structure_type = {"list" : ast.List, "tuple": ast.Tuple, "dict": ast.Dict, "set": ast.Set}
        
    @property
    def tree(self:Self) -> ast.Module:
        """
        L'arbre syntaxique en cours de construction.

        Returns:
            ast.Module: Le nœud racine de l'AST courant, ou None si le
                constructeur n'a pas encore été initialisé.
        """
        return self._tree

    def reset(self:Self) -> None:
        """
        Réinitialise le constructeur à son état initial.

        Remet à zéro l'arbre syntaxique, le dictionnaire des racines courantes,
        l'identifiant de la première racine et la liste des variables de classe,
        permettant la construction d'un nouvel AST.
        """
        self._tree = None
        self._current_root = {}
        self._first_root_id = None
        self._root_variable = []

    def create_tree(self:Self, data:List[Dict[str, Any]]) -> None:
        """
        Initialise la structure racine de l'AST et configure le validateur.

        Crée un nœud `ast.Module` vide et configure l'`ASTValidator` avec
        les données du graphe nodal pour préparer la validation.

        Args:
            data (Dict[str, Any]): Les données du graphe nodal nécessaires
                à la configuration du validateur.
        """
        self._tree = ast.Module(body=[], type_ignores=[])
        self._ast_validator.config(data)

    def get_ast(self:Self) -> ast.Module:
        """
        Retourne l'AST complet et réinitialise le constructeur.

        Récupère l'arbre syntaxique finalisé puis appelle `reset` pour
        préparer le constructeur à une nouvelle utilisation.

        Returns:
            ast.Module: L'arbre syntaxique finalisé et prêt à être utilisé.
        """
        tree = self._tree
        self.reset()
        return tree
    
    def build_import(self:Self, data:List[Dict[str, Any]]) -> None:
        """
        Construit et ajoute les nœuds d'importation à l'AST.

        Génère les imports statiques requis par toute application PySide6
        ainsi que les imports dynamiques déduits des composants du graphe
        nodal, puis les ajoute à l'AST.

        Args:
            data (List[Dict[str, Any]]): Les données du graphe nodal
                nécessaires à la génération des imports dynamiques.
        """
        import_buffers = {"system": set(), "qt":{}, "feature":{}, "local":{}}
        self._add_static_import(import_buffers)

        self._add_dynamic_import(data, import_buffers)

        self._build_import_nodes(import_buffers)

    def build_class(self:Self, data:List[Dict[str, Any]], data_dict:Dict[str, Any]) -> None:
        """
        Construit et ajoute les nœuds de définition de classe à l'AST.

        Identifie les composants racines, génère leurs nœuds de classe,
        attache les métadonnées de validation, puis construit le `__init__`
        et les fonctions utilisateur de chaque classe.

        Args:
            data (Dict[str, Any]): Les données complètes du graphe nodal.
            data_dict (Dict[str, Any]): Le dictionnaire des composants indexés
                par identifiant.
        """
        component = data["components"]
        root_list = self._find_root(component)
        self._build_class_node(root_list, data_dict)

        for node_id, node in self._current_root.items():
            if not self._first_root_id:
                self._first_root_id = node_id
            self._ast_validator.insert_details(node, node_id)
            self._build_init_node(node_id, node, data, data_dict)
            self._build_function(node.body, data_dict[node_id]["function"], node_id)

    def build_main(self:Self, data_dict:Dict[str, Any]) -> None:
        """
        Construit et ajoute la fonction principale et le bloc `if __name__ == "__main__"`.

        Génère la fonction `main` contenant l'instanciation de la `QApplication`,
        du widget principal et l'appel à `sys.exit`, ainsi que le bloc
        `if __name__ == "__main__"` appelant cette fonction.

        Args:
            data_dict (Dict[str, Any]): Le dictionnaire des composants indexés
                par identifiant, utilisé pour déterminer le type du widget principal.
        """
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

        self._ast_validator.insert_details(if_main_node, "__main__")

        self._tree.body.append(if_main_node)
                                                
    def _build_class_node(self:Self, root_list:List[str], data_dict:Dict[str, Any]) -> None:
        """
        Crée les nœuds de définition de classe pour chaque composant racine.

        Génère un nœud `ast.ClassDef` pour chaque composant racine avec son
        nom et ses classes parentes, l'ajoute à l'AST et l'enregistre dans
        `_current_root`.

        Args:
            root_list (List[str]): La liste des identifiants des composants racines.
            data_dict (Dict[str, Any]): Le dictionnaire des composants indexés
                par identifiant.
        """
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
    
    def _build_init_node(self:Self, class_node_id:str, class_node:ast.AST, data:List[Dict[str, Any]], data_dict:Dict[str, Any]) -> None:
        """
        Crée et ajoute le nœud `__init__` à un nœud de classe.

        Génère la définition de la méthode `__init__` avec les paramètres
        `self` et `parent`, puis délègue la construction de son corps à
        `_build_init_body`.

        Args:
            class_node_id (str): L'identifiant du composant correspondant à la classe.
            class_node (ast.ClassDef): Le nœud de classe auquel ajouter le `__init__`.
            data (Dict[str, Any]): Les données complètes du graphe nodal.
            data_dict (Dict[str, Any]): Le dictionnaire des composants indexés
                par identifiant.
        """
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
        
    def _build_init_body(self:Self, class_node_id:str, body:List[Any], data:List[Dict[str, Any]], data_dict:Dict[str, Any]) -> None:  
        """
        Construit le corps de la méthode `__init__`.

        Génère dans l'ordre : l'appel à `super().__init__()`, l'initialisation
        des variables de classe, l'application des propriétés, la construction
        de la hiérarchie des widgets et les connexions de signaux.

        Args:
            class_node_id (str): L'identifiant du composant correspondant à la classe.
            body (List[ast.stmt]): Le corps de la méthode `__init__` à peupler.
            data (Dict[str, Any]): Les données complètes du graphe nodal.
            data_dict (Dict[str, Any]): Le dictionnaire des composants indexés
                par identifiant.
        """
        body.append(self._build_super_init_node())
        self._build_init_variable(class_node_id, body, data_dict)
        self._build_properties(body, data_dict[class_node_id]["properties"], ast.Name(id="self", ctx=ast.Load()), data_dict)
        self._build_hierarchy(class_node_id, data_dict[class_node_id], body, data, data_dict)
        self._build_links(class_node_id, body, data, data_dict)

    def _build_super_init_node(self:Self) -> ast.Expr:
        """
        Crée le nœud d'appel à `super().__init__(parent)`.

        Returns:
            ast.Expr: Le nœud d'expression représentant l'appel à l'initialiseur
                de la classe parente.
        """
        super_node = ast.Name(id="super", ctx=ast.Load())
        parent_node = ast.Name(id="parent", ctx=ast.Load())
        super_call = ast.Call(func=super_node, args=[], keywords=[])

        init_func = ast.Attribute(value=super_call, attr="__init__", ctx=ast.Load())
        init_call = ast.Call(func = init_func, args=[parent_node], keywords=[])
        
        return ast.Expr(value = init_call)

    def _build_init_variable(self:Self, class_node_id:str, body:List[Any], data_dict:Dict[str, Any]) -> None:
        """
        Construit les nœuds d'assignation des variables de classe dans `__init__`.

        Génère les assignations `self.nom_variable = valeur` pour chaque variable
        du composant. Les variables référençant un autre composant via un `id`
        sont ajoutées à `_root_variable` et placées avant les autres variables
        dans le corps du `__init__`.

        Args:
            class_node_id (str): L'identifiant du composant correspondant à la classe.
            body (List[ast.stmt]): Le corps de la méthode `__init__` à peupler.
            data_dict (Dict[str, Any]): Le dictionnaire des composants indexés
                par identifiant.
        """
        root_data = data_dict[class_node_id]
        components_nodes = []
        variables_nodes = []

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

    def _process_variable_value(self:Self, var:Dict[str, Any], data_dict:Dict[str, Any]) -> ast.Expr | None:
        """
        Convertit une valeur de variable du graphe nodal en nœud AST.

        Traite les types primitifs, les références à d'autres composants,
        les structures Python, les énumérations, les flags et les expressions
        brutes.

        Args:
            var (Dict[str, Any]): La variable à convertir, contenant son type
                et sa valeur.
            data_dict (Dict[str, Any]): Le dictionnaire des composants indexés
                par identifiant, utilisé pour résoudre les références.

        Returns:
            ast.Expr | None: Le nœud AST correspondant à la valeur, ou None
                si le type n'est pas reconnu.
        """
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
        
    def _add_static_import(self:Self, import_buffers:Dict[str, List | Set]) -> None:
        """
        Ajoute les imports statiques requis par toute application PySide6.

        Ajoute systématiquement `sys`, `QApplication` et les features PySide6
        (`snake_case`, `true_property`) aux buffers d'imports.

        Args:
            import_buffers (Dict[str, Any]): Le dictionnaire des buffers
                d'imports à peupler.
        """
        import_buffers["system"].add("sys")
        import_buffers["qt"]["PySide6.QtWidgets"] = set(("QApplication",))
        import_buffers["feature"]["__feature__"] = set(("snake_case", "true_property"))

    def _add_dynamic_import(self:Self, components:List[Dict[str, Any]], import_buffers:Dict[str, List | Set]) -> None:
        """
        Déduit et ajoute les imports dynamiques à partir des composants du graphe nodal.

        Extrait les données de modules, d'héritage et de propriétés des composants
        pour déterminer les imports Qt, système et locaux nécessaires.

        Args:
            components (List[Dict[str, Any]]): La liste des composants du graphe nodal.
            import_buffers (Dict[str, Any]): Le dictionnaire des buffers
                d'imports à peupler.
        """
        data = self._find_data(("module", "inheritance", "properties"), components)
        self._process_system_data(data, import_buffers["system"])
        self._process_qt_data(data, import_buffers["qt"])
        self._process_local_data(data, import_buffers["local"])

    def _find_data(self:Self, keys: Tuple[str], data_list: Dict[str, Any]) -> List[Any]:
        """
        Extrait les éléments d'une liste de données selon une liste de clés.

        Parcourt chaque élément de `data_list` et collecte les valeurs
        correspondant aux clés spécifiées, qu'elles soient des chaînes ou
        des listes.

        Args:
            keys (tuple[str]): Les clés à rechercher dans chaque élément.
            data_list (dict[str, list | str]): La liste des éléments à parcourir.

        Returns:
            List: La liste aplatie des éléments extraits.
        """
        items = []

        for item in data_list:
            for key in keys:
                if item.get(key):
                    if isinstance(item.get(key), str):
                        items.append(item)
                    elif isinstance(item.get(key), list):
                        items.extend(item[key])

        return items
    
    def _process_qt_data(self:Self, extracted_data:List[Dict[str, Any]], target_buffer:Dict[str, Set]):
        """
        Peuple le buffer d'imports Qt à partir des données extraites.

        Pour chaque élément, détermine le module et le type Qt à importer
        selon qu'il s'agit d'un composant avec module ou d'une propriété
        avec namespace. Ignore les composants de catégorie `custom`.

        Args:
            extracted_data (List[Dict[str, Any]]): Les données extraites par `_find_data`.
            target_buffer (Dict[str, Set]): Le buffer d'imports Qt à peupler.
        """
        for item in extracted_data:
            target_key = None
            target_value = None

            if item.get("category") == "custom":
                continue
            if item.get("module"):
                target_key = item["module"]
                target_value = item["type"]
            elif item.get("namespace"):
                target_key = item["namespace"][0]
                target_value = item["namespace"][1]

            if target_key and target_value:
                target_buffer.setdefault(target_key, set()).add(target_value)

    def _process_system_data(self:Self, json_data: List[Dict[str,Any]], import_data:Set[str]) -> None:
        """
        Peuple le buffer d'imports système à partir des données extraites.

        Args:
            json_data (List[Dict[str, Any]]): Les données extraites par `_find_data`.
            import_data (Set[str]): Le buffer d'imports système à peupler.
        """
        ...

    def _process_local_data(self:Self, json_data: List[Dict[str,Any]], import_data:Dict[str, Set]) -> None:
        """
        Peuple le buffer d'imports locaux à partir des données extraites.

        Args:
            json_data (List[Dict[str, Any]]): Les données extraites par `_find_data`.
            import_data (Dict[str, Set]): Le buffer d'imports locaux à peupler.
        """
        ...

    def _build_import_nodes(self:Self, import_buffers:Dict[str, Any]) -> None:
        """
        Génère et ajoute les nœuds d'importation à l'AST.

        Convertit les buffers d'imports en nœuds `ast.Import` ou
        `ast.ImportFrom` selon leur structure et les ajoute à l'AST.

        Args:
            import_buffers (Dict[str, Any]): Le dictionnaire des buffers
                d'imports à convertir.

        Raises:
            TypeError: Si le format d'un buffer d'import n'est pas reconnu.
        """
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
            
    def _find_root(self:Self, data:List[Dict[str, Any]]):
        """
        Identifie les composants racines du graphe nodal.

        Détermine les composants racines en calculant la différence entre
        l'ensemble de tous les identifiants et l'ensemble des identifiants
        référencés comme enfants.

        Args:
            data (List[Dict[str, Any]]): La liste des composants du graphe nodal.

        Returns:
            List[str]: La liste des identifiants des composants racines.
        """
        child_set = set()
        id_set = set()

        for component in data:
            child_set.update(component["child"])
            id_set.add(component["id"])
        
        return list(id_set.difference(child_set))

    def _build_properties(self:Self, node: List[Any], properties: List[Dict[str, Any]], target_name:str, data_dict:Dict[str, Any]) -> None:
        """
        Construit et ajoute les nœuds d'assignation des propriétés à un nœud AST.

        Pour chaque propriété, génère un nœud d'assignation `target.propriété = valeur`.
        Si la valeur ne peut pas être résolue directement, génère un appel
        au constructeur du type Qt correspondant avec des arguments nommés.

        Args:
            node (List[ast.stmt]): Le corps du nœud AST à peupler.
            properties (List[Dict[str, Any]]): La liste des propriétés à construire.
            target_name (ast.expr): Le nœud AST représentant la cible de l'assignation.
            data_dict (Dict[str, Any]): Le dictionnaire des composants indexés
                par identifiant.
        """
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

    def _build_flag_value(self:Self, flag_value:Dict[str, Any], property_namespace:List[str]) -> ast.Expr:
        """
        Construit le nœud AST représentant une valeur de type flag Qt.

        Combine les valeurs exclusives et non exclusives du flag en une
        expression binaire utilisant l'opérateur `|` (BitOr).

        Args:
            flag_value (Dict[str, Any]): Le dictionnaire contenant les valeurs
                exclusives et non exclusives du flag.
            property_namespace (List[str]): Le namespace de la propriété
                contenant le module, la classe et l'énumération.

        Returns:
            ast.Expr: Le nœud AST représentant la valeur du flag.
        """
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

    def _build_property_value(self:Self, child_name:str, parent_name:str, value:str) -> ast.Attribute:
        """
        Construit le nœud AST représentant un accès à une valeur d'énumération Qt.

        Génère une expression de la forme `parent_name.child_name.value`
        correspondant typiquement à un accès à une valeur d'énumération Qt
        (ex: `Qt.AlignmentFlag.AlignLeft`).

        Args:
            child_name (str): Le nom de la classe enfant (ex: 'AlignmentFlag').
            parent_name (str): Le nom du module parent (ex: 'Qt').
            value (str): La valeur de l'énumération (ex: 'AlignLeft').

        Returns:
            ast.Attribute: Le nœud AST représentant l'accès à la valeur.
        """
        return ast.Attribute(
                    value = ast.Attribute(
                        value = ast.Name(id=parent_name, ctx=ast.Load()),
                        attr = child_name,
                        ctx = ast.Load()
                    ),
                    attr = value,
                    ctx = ast.Load()
                )
    
    def _build_function(self:Self, body:List[ast.stmt], functions:List[Any], node_id:str) -> None:
        """
        Construit et ajoute les nœuds de définition des fonctions utilisateur.

        Ignore les fonctions internes (`is_intern = True`). Pour chaque fonction
        utilisateur, parse son code, génère un nœud `ast.FunctionDef` et
        l'ajoute au corps de la classe. Si le corps est vide, un nœud `Pass`
        est inséré.

        Args:
            body (List[ast.stmt]): Le corps du nœud de classe à peupler.
            functions (List[Dict[str, Any]]): La liste des fonctions à construire.
            node_id (str): L'identifiant du composant correspondant à la classe.
        """
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

    def _build_links(self:Self, root_id:str, body:List[ast.stmt], data:Dict[str, Any], data_dict:Dict[str, Any]) -> None:
        """
        Construit et ajoute les nœuds de connexion de signaux Qt à l'AST.

        Pour chaque lien du graphe nodal, génère un appel
        `source.signal.connect(target.slot)` en résolvant les noms et parents
        de chaque composant source et cible.

        Args:
            root_id (str): L'identifiant du composant racine de la classe courante.
            body (List[ast.stmt]): Le corps du `__init__` à peupler.
            data (Dict[str, Any]): Les données complètes du graphe nodal.
            data_dict (Dict[str, Any]): Le dictionnaire des composants indexés
                par identifiant.
        """
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

    def _build_hierarchy(self:Self, root_id:str, root_node:Dict[str, Any], body:List[ast.stmt], data:Dict[str, Any], data_dict:Dict[str, Any]) -> None:
        """
        Construit récursivement la hiérarchie des widgets Qt dans le `__init__`.

        Pour chaque enfant du composant courant, génère l'instanciation du
        widget si nécessaire, appelle `_generate_qt_add_method` pour l'ajouter
        à son parent, puis récurse sur ses propres enfants.

        Args:
            root_id (str): L'identifiant du composant courant.
            root_node (Dict[str, Any]): Les données du composant racine de la classe.
            body (List[ast.stmt]): Le corps du `__init__` à peupler.
            data (Dict[str, Any]): Les données complètes du graphe nodal.
            data_dict (Dict[str, Any]): Le dictionnaire des composants indexés
                par identifiant.
        """
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

    def _generate_qt_add_method(self:Self, parent_id:str, child_id:str, body:List[ast.stmt], data_dict:Dict[str, Any]) -> None:
        """
        Génère l'appel à la méthode Qt appropriée pour ajouter un enfant à son parent.

        Détermine la méthode à appeler (`set_layout`, `add_widget` ou `add_layout`)
        selon les catégories du parent et de l'enfant, puis génère le nœud
        d'appel correspondant.

        Args:
            parent_id (str): L'identifiant du composant parent.
            child_id (str): L'identifiant du composant enfant.
            body (List[ast.stmt]): Le corps du `__init__` à peupler.
            data_dict (Dict[str, Any]): Le dictionnaire des composants indexés
                par identifiant.
        """
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