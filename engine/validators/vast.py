"""
Validateurs d'AST pour le moteur SyntaxNode.

Ce module fournit les outils d'analyse et de validation de l'arbre syntaxique
généré à partir du graphe nodal. Il détecte les références invalides, les
variables inconnues et les fonctions potentiellement malveillantes dans le
code utilisateur.

Classes
-------
FunctionValidator: Validateur de références et de sécurité dans les fonctions utilisateur.
ASTValidator: Orchestrateur de la validation de l'AST complet.
"""

import ast
import importlib
import builtins
from typing import List, Dict, Any, Self, override
from ..error import CodeReferenceError, ErrorContainer, IllegalImportError, ErrorDetails, FatalError

from __feature__ import true_property, snake_case #type: ignore[import-not-found]

class FunctionValidator(ast.NodeVisitor):
    """
    Validateur de références et de sécurité dans les fonctions utilisateur.

    Parcourt l'AST à la recherche de variables inconnues, de fonctions non
    définies et de fonctions potentiellement malveillantes. Hérite de
    `ast.NodeVisitor` pour traverser l'arbre nœud par nœud.

    Attributes:
        _BUILTIN_FUNCTIONS (set): L'ensemble des fonctions natives Python autorisées.
        _BLACK_LIST (set): L'ensemble des identifiants potentiellement malveillants
            dont l'utilisation est interdite.
        _error_details_list (List[ErrorDetails]): La liste des erreurs accumulées
            lors de la traversée.
        _error_type (type): Le type d'exception à lever en cas d'erreurs détectées.
        _valid_variable (set): Les variables de classe valides pour le composant courant.
        _valid_function (set): Les fonctions valides pour le composant courant.
        _local_variable (set): Les variables locales à la fonction courante.
        _is_init_function (bool): Indique si la fonction courante est `__init__`,
            où les règles de validation sont assouplies.
        _class_node (ast.ClassDef): Le nœud de classe couramment analysé.
        _target_attribute_visitor (_TargetAttributeVisitor): Le visiteur auxiliaire
            pour l'extraction des attributs cibles.
    """
    _BUILTIN_FUNCTIONS = set(func_name for func_name, func in builtins.__dict__.items() if callable(func))
    _BLACK_LIST = set(["eval", "exec", "compile", "open", "__import__", "__builtins__", "__globals__", "__class__", "__subclasses__", "sys"])
    

    def __init__(self:Self) -> None:
        """
        Initialise le validateur avec des ensembles vides et un état par défaut.

        L'état `_is_init_function` est initialisé à `True` pour éviter toute
        validation prématurée avant la première visite d'une fonction.
        """
        self._error_details_list = []
        self._error_type = CodeReferenceError
        self._valid_variable = set()
        self._valid_function = set()
        self._local_variable = set()
        self._is_init_function = True
        self._class_node = None

        self._target_attribute_visitor = _TargetAttributeVisitor()
  
    @override
    def visit_ClassDef(self:Self, node:ast.ClassDef) -> None:
        """
        Visite un nœud de définition de classe et initialise le contexte de validation.

        Extrait les variables et fonctions valides préalablement attachées au nœud
        par `ASTValidator.insert_details` et met à jour le nœud de classe courant.

        Args:
            node (ast.ClassDef): Le nœud de classe à visiter.
        """
        self._valid_variable = getattr(node, "sn_local_variable", []).copy()
        self._valid_function = getattr(node, "sn_local_function", []).copy()
        self._class_node = node
        self.generic_visit(node)

    @override
    def visit_FunctionDef(self: Self, node:ast.FunctionDef) -> None:
        """
        Visite un nœud de définition de fonction et initialise le contexte local.

        Réinitialise les variables locales, détermine si la fonction courante est
        `__init__` et extrait les paramètres comme variables locales valides.
        La fonction `main` est ignorée car elle est générée automatiquement par
        le moteur et ne contient pas de code utilisateur.

        Args:
            node (ast.FunctionDef): Le nœud de fonction à visiter.
        """
        self._local_variable = set()
        self._is_init_function = node.name == "__init__"
        param_names = {param.arg for param in node.args.args}
        self._local_variable.update(param_names)

        if node.name != "main":
            self.generic_visit(node)

    @override
    def visit_Assign(self:Self, node:ast.Assign) -> None:
        """
        Visite un nœud d'assignation et valide les cibles et la valeur assignées.

        Catégorise chaque cible comme variable locale, variable de classe valide
        dans `__init__`, ou lève une erreur si une variable de classe est créée
        dans une fonction autre que `__init__`.

        Args:
            node (ast.Assign): Le nœud d'assignation à visiter.

        Raises:
            FatalError: Si une fonction potentiellement malveillante est détectée
                dans la valeur assignée.
        """
        for target in node.targets:
            self._target_attribute_visitor._attribute = ""
            self._target_attribute_visitor._is_local = True
            self._target_attribute_visitor.visit(target)
            if self._target_attribute_visitor._is_local:
                self._local_variable.add(self._target_attribute_visitor._attribute)
            elif self._is_init_function:
                self._valid_variable.add(self._target_attribute_visitor._attribute)
            elif self._target_attribute_visitor._attribute not in (self._valid_variable | self._local_variable):
                sn_loc = getattr(self._class_node, "sn_loc", [])
                sn_id = getattr(self._class_node, "sn_id", "")
                msg = f"Création de variable de classe interdite dans les fonctions. Variable : {self._target_attribute_visitor._attribute} invalide"
                user_msg = f"Création de variable de classe interdite dans les fonctions."
                error_detail = ErrorDetails(sn_loc, msg, sn_id, user_msg)
                self._error_details_list.append(error_detail)

        self.visit(node.value)

    @override
    def visit_Name(self:Self, node:ast.Name) -> None:
        """
        Visite un nœud de référence à un identifiant et valide son existence.

        Ignore les références dans `__init__` et les références à `self`. Lève
        une `FatalError` immédiatement si l'identifiant est dans la liste noire,
        ou accumule une erreur si l'identifiant est inconnu dans le contexte
        courant.

        Args:
            node (ast.Name): Le nœud d'identifiant à visiter.

        Raises:
            FatalError: Si l'identifiant est potentiellement malveillant.
        """
        if self._is_init_function or node.id == "self":
            return
        elif node.id in FunctionValidator._BLACK_LIST:
            sn_loc = getattr(self._class_node, "sn_loc", [])
            sn_id = getattr(self._class_node, "sn_id", "")
            msg = f"Fonction potentiellement malveillante, requête refusée"
            user_msg = f"Une erreur est survenue. Impossible de traiter la requête."
            error_detail = ErrorDetails(sn_loc, msg, sn_id, user_msg)
            raise FatalError(error_detail)
        elif node.id not in (self._local_variable | self._valid_variable):
            msg = f"variable {node.id} inconnue"
            error_detail = ErrorDetails(self._class_node.sn_loc, msg, self._class_node.sn_id, msg)
            self._error_details_list.append(error_detail)

    @override
    def visit_Call(self:Self, node:ast.Call) -> None:
        """
        Visite un nœud d'appel de fonction et valide son existence dans le contexte courant.

        Ignore les appels dans `__init__`. Accumule une erreur si la fonction
        appelée n'est pas connue parmi les fonctions valides, les fonctions
        natives Python, les variables locales ou les variables de classe.
        Visite ensuite récursivement les arguments de l'appel.

        Args:
            node (ast.Call): Le nœud d'appel de fonction à visiter.
        """
        if self._is_init_function:
            return
        self._target_attribute_visitor.visit(node.func)
        func_name = self._target_attribute_visitor._attribute
        if func_name not in (self._valid_function | self._BUILTIN_FUNCTIONS | self._local_variable | self._valid_variable):
            sn_loc = getattr(self._class_node, "sn_loc", [])
            sn_id = getattr(self._class_node, "sn_id", "")
            msg = f"L'identifiant {func_name} inconnue"
            error_detail = ErrorDetails(sn_loc, msg, sn_id, msg)
            self._error_details_list.append(error_detail)
        for func_arg in node.args:
            self.generic_visit(func_arg)

    @override
    def visit_If(self:Self, node:ast.Compare) -> None:
        """
        Visite un nœud conditionnel et ignore le bloc `if __name__ == "__main__"`.

        Ce bloc est généré automatiquement par le moteur et ne contient pas de
        code utilisateur, il n'a donc pas besoin d'être validé.

        Args:
            node (ast.Compare): Le nœud conditionnel à visiter.
        """
        node_id = getattr(node, "sn_id", "")
        if node_id and node_id == "__main__":
            return
        else:
            self.generic_visit(node)
        
class _TargetAttributeVisitor(ast.NodeVisitor):
    """
    Visiteur auxiliaire pour l'extraction du nom complet d'une cible d'assignation.

    Utilisé par `FunctionValidator` pour déterminer si une cible d'assignation
    est une variable locale ou un attribut de classe (ex: `self.mon_attribut`),
    et extraire son nom complet.

    Attributes:
        _attribute (str): Le nom complet de l'attribut extrait (ex: 'self.mon_attribut').
        _is_local (bool): Indique si la cible est une variable locale (True)
            ou un attribut de classe via `self` (False).
    """
    def __init__(self:Self) -> None:
        """
        Initialise le visiteur avec un attribut vide et un état local par défaut.
        """
        self._attribute = ""
        self._is_local = True
        

    @override
    def visit_Attribute(self:Self, node:ast.Attribute) -> None:
        """
        Visite un nœud d'accès à un attribut et construit le nom complet.

        Si la cible de base est `self`, concatène le nom de l'attribut pour
        former le nom complet (ex: `self.mon_attribut`).

        Args:
            node (ast.Attribute): Le nœud d'attribut à visiter.
        """
        self.generic_visit(node)
        if self._attribute == "self":
            self._attribute += f".{node.attr}"

    @override
    def visit_Name(self:Self, node:ast.Name) -> None:
        """
        Visite un nœud d'identifiant et détermine si la cible est locale ou un attribut de classe.

        Met à jour `_attribute` avec le nom de l'identifiant et `_is_local` selon
        que l'identifiant est `self` ou non.

        Args:
            node (ast.Name): Le nœud d'identifiant à visiter.
        """
        self._attribute = node.id
        self._is_local = node.id != "self"
        

class ASTValidator:
    """
    Orchestrateur de la validation de l'AST complet.

    Configure le contexte de validation à partir des données du graphe nodal,
    attache les métadonnées SyntaxNode aux nœuds de l'AST et orchestre
    l'exécution des validateurs sur l'arbre syntaxique complet.

    Attributes:
        _loc_dict (dict): Le dictionnaire associant chaque identifiant de
            composant à son emplacement dans la structure JSON.
        _local_variable (dict): Le dictionnaire associant chaque identifiant
            de composant à ses variables valides.
        _local_function (dict): Le dictionnaire associant chaque identifiant
            de composant à ses fonctions valides.
        _validators (tuple): L'ensemble des validateurs à exécuter sur l'AST.
    """
    def __init__(self:Self) -> None:
        """
        Initialise le validateur avec des dictionnaires vides et un `FunctionValidator`
        comme validateur par défaut.
        """
        self._loc_dict = {}
        self._local_variable = {}
        self._local_function = {}
        self._validators = (FunctionValidator(),)
    
    def insert_details(self:Self, node:ast.AST, node_id:str) -> None:
        """
        Attache les métadonnées SyntaxNode à un nœud de l'AST.

        Enrichit le nœud avec son identifiant, son emplacement dans la structure
        JSON, ainsi que ses variables et fonctions valides. Le nœud `__main__`
        est traité différemment car il est généré automatiquement par le moteur
        et ne nécessite pas de métadonnées de validation.

        Args:
            node (ast.AST): Le nœud de l'AST à enrichir.
            node_id (str): L'identifiant du composant correspondant.
        """
        node.sn_id = node_id

        if node_id == "__main__":
            return
        
        node.sn_loc = self._loc_dict[node_id]
        node.sn_local_variable = self._local_variable[node_id]
        node.sn_local_function = self._local_function[node_id]

    def config(self:Self, data: List[Dict[str, Any]]) -> None:
        """
        Configure le validateur à partir des données du graphe nodal.

        Réinitialise les dictionnaires internes et extrait les détails de
        validation de chaque composant via `_extract_details`.

        Args:
            data (List[Dict[str, Any]]): Le graphe nodal configuré par l'utilisateur.
        """
        self._loc_dict = {}
        self._extract_details(data)

    def validate_data(self:Self, tree: ast.AST) -> None:
        """
        Exécute tous les validateurs sur l'AST et lève les erreurs détectées.

        Réinitialise l'état de chaque validateur avant la traversée. Si des
        erreurs sont accumulées après la visite, elles sont regroupées dans
        un `ErrorContainer` et levées en une seule exception.

        Args:
            tree (ast.AST): L'arbre syntaxique à valider.

        Raises:
            FatalError: Si une fonction potentiellement malveillante est détectée.
            ErrorContainer: Si des erreurs de validation sont détectées.
        """
        error_list = []
        for validator in self._validators:
            validator._error_details_list = []
            validator._is_init_function = True
            validator.visit(tree)

            if validator._error_details_list:
                error_list.append(validator._error_type(validator._error_details_list))

        if error_list:
            raise ErrorContainer(error_list)

    def _extract_details(self:Self, data: Dict[str, Any]) -> None:
        """
        Extrait et stocke les détails de validation de chaque composant.

        Méthode interne destinée à être appelée par `config`. Pour chaque
        composant, introspecte la classe héritée via `importlib` pour extraire
        les attributs et méthodes valides, puis complète avec les variables et
        fonctions définies par l'utilisateur dans le graphe nodal.

        Args:
            data (Dict[str, Any]): Les données du graphe nodal.

        Raises:
            IllegalImportError: Si un module requis par un composant ne peut
                pas être importé.
        """
        for i, component in enumerate(data.get("components", [])):
            loc = ["components", str(i), "id"]
            self._loc_dict[component["id"]] = loc
            self._local_variable[component["id"]] = set()
            self._local_function[component["id"]] = set()

            inheritance = component["inheritance"]
            if inheritance:
                inheritance = inheritance[0]
                module_name = inheritance["module"]
                class_name = inheritance["type"]
            else:
                module_name = component["module"]
                class_name = component["type"]

            try:
                obj_module = importlib.import_module(module_name)
                obj_class = getattr(obj_module, class_name)
                inherited_attr = dir(obj_class)
                for attr in inherited_attr:
                    if callable(getattr(obj_class, attr)) and not attr.startswith("__"):
                        self._local_function[component["id"]].add(f"self.{attr}")
                    else:
                        self._local_variable[component["id"]].add(f"self.{attr}")
            except Exception as e:
                error_detail = ErrorDetails(loc, f"Impossible d'importer {class_name} du module {module_name}", component["id"], f"Il n'est pas possible de faire des imports à l'intérieur des fonctions.")
                raise IllegalImportError([error_detail])

            for variable in component.get("variable", []):
                self._local_variable[component["id"]].add(f"self.{variable.get('name')}")

            for function in component.get("function", []):
                self._local_function[component["id"]].add(f"self.{function.get('name')}")
