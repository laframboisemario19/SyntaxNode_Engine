"""
CODE GÉNÉRÉ PAR CLAUDE POUR GÉNÉRER DES JSON SYNTAXNODE AUTOMATIQUEMENT POUR LE DATASET.

Générateur de dataset SyntaxNode pour l'entraînement PyTorch.
Produit des projets JSON sains et malsains pour 4 patterns de bugs :
  - infinite_loop  : boucle while sans incrémentation
  - div_zero       : division par un spinbox avec minimum=0
  - undef_var      : variable non définie dans une branche if/elif sans else
  - dup_params     : paramètres dupliqués dans une fonction
"""

import json
import os
import random
import copy
from pathlib import Path

random.seed(42)

OUT_CLEAN   = Path("output/bugs/clean")
OUT_UNCLEAN = Path("output/bugs/unclean")
OUT_CLEAN.mkdir(parents=True, exist_ok=True)
OUT_UNCLEAN.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Vocabulaire de variation
# ---------------------------------------------------------------------------

APP_NAMES = [
    "CalculatorApp", "DashboardApp", "SettingsApp", "ProfileApp", "ReportApp",
    "MonitorApp", "TrackerApp", "PlannerApp", "EditorApp", "ViewerApp",
    "FormApp", "ToolApp", "PanelApp", "ConsoleApp", "ExplorerApp",
    "AnalyzerApp", "BuilderApp", "ManagerApp", "ScannerApp", "FilterApp",
]

PROJECT_NAMES = [
    "calculator", "dashboard", "settings_panel", "user_profile", "report_viewer",
    "system_monitor", "task_tracker", "event_planner", "text_editor", "data_viewer",
    "contact_form", "dev_tool", "control_panel", "debug_console", "file_explorer",
    "log_analyzer", "config_builder", "asset_manager", "port_scanner", "data_filter",
]

WINDOW_TITLES = [
    "Calculatrice", "Tableau de bord", "Paramètres", "Profil utilisateur",
    "Visionneuse", "Moniteur système", "Suivi des tâches", "Planificateur",
    "Éditeur de texte", "Explorateur", "Formulaire de contact", "Outil",
    "Panneau de contrôle", "Console", "Analyseur", "Gestionnaire",
    "Configurateur", "Scanner", "Filtre de données", "Rapport",
]

# Widgets numériques (pour div_zero et loop)
NUMERIC_WIDGETS = [
    {
        "type": "QSpinBox",
        "module": "PySide6.QtWidgets",
        "category": "widget",
        "value_prop": "value",
        "extra_props_clean": [
            {"name": "minimum", "type": "int", "value": 1},
            {"name": "maximum", "type": "int", "value": 100},
            {"name": "value",   "type": "int", "value": 10},
        ],
        "extra_props_unclean_divzero": [
            {"name": "minimum", "type": "int", "value": 0},
            {"name": "maximum", "type": "int", "value": 100},
            {"name": "value",   "type": "int", "value": 10},
        ],
    },
    {
        "type": "QSpinBox",
        "module": "PySide6.QtWidgets",
        "category": "widget",
        "value_prop": "value",
        "extra_props_clean": [
            {"name": "minimum", "type": "int", "value": 2},
            {"name": "maximum", "type": "int", "value": 50},
            {"name": "value",   "type": "int", "value": 5},
            {"name": "suffix",  "type": "str", "value": " unités"},
        ],
        "extra_props_unclean_divzero": [
            {"name": "minimum", "type": "int", "value": 0},
            {"name": "maximum", "type": "int", "value": 50},
            {"name": "value",   "type": "int", "value": 5},
            {"name": "suffix",  "type": "str", "value": " unités"},
        ],
    },
    {
        "type": "QSpinBox",
        "module": "PySide6.QtWidgets",
        "category": "widget",
        "value_prop": "value",
        "extra_props_clean": [
            {"name": "minimum", "type": "int", "value": 1},
            {"name": "maximum", "type": "int", "value": 200},
            {"name": "value",   "type": "int", "value": 20},
            {"name": "prefix",  "type": "str", "value": "N : "},
        ],
        "extra_props_unclean_divzero": [
            {"name": "minimum", "type": "int", "value": 0},
            {"name": "maximum", "type": "int", "value": 200},
            {"name": "value",   "type": "int", "value": 20},
            {"name": "prefix",  "type": "str", "value": "N : "},
        ],
    },
]

# Widgets d'affichage texte
DISPLAY_WIDGETS = [
    {"type": "QLabel",    "module": "PySide6.QtWidgets", "text": "Résultat : —"},
    {"type": "QLabel",    "module": "PySide6.QtWidgets", "text": "En attente..."},
    {"type": "QLabel",    "module": "PySide6.QtWidgets", "text": ""},
    {"type": "QLabel",    "module": "PySide6.QtWidgets", "text": "Prêt."},
]

# Boutons
BUTTON_LABELS = [
    "Calculer", "Lancer", "Valider", "Confirmer", "Exécuter",
    "Analyser", "Appliquer", "Démarrer", "Traiter", "Soumettre",
    "Générer", "Vérifier", "Compiler", "Tester", "Envoyer",
]

# Layouts
LAYOUT_TYPES = [
    {"type": "QVBoxLayout", "module": "PySide6.QtWidgets"},
    {"type": "QHBoxLayout", "module": "PySide6.QtWidgets"},
]

# Mentions pour undef_var
MENTION_SETS = [
    {
        "thresholds": [(90, "Excellent"), (70, "Bien"), (50, "Passable")],
        "var": "mention",
        "display": "Résultat : {mention}",
        "spin_suffix": " %",
        "spin_max": 100,
        "spin_val_clean": 75,
        "spin_val_unclean": 30,
    },
    {
        "thresholds": [(80, "Approuvé"), (60, "Acceptable")],
        "var": "statut",
        "display": "Statut : {statut}",
        "spin_suffix": " pts",
        "spin_max": 100,
        "spin_val_clean": 70,
        "spin_val_unclean": 40,
    },
    {
        "thresholds": [(95, "Parfait"), (75, "Bon"), (55, "Moyen")],
        "var": "niveau",
        "display": "Niveau : {niveau}",
        "spin_suffix": " %",
        "spin_max": 100,
        "spin_val_clean": 80,
        "spin_val_unclean": 20,
    },
    {
        "thresholds": [(100, "Maximum"), (50, "Moyen")],
        "var": "categorie",
        "display": "Catégorie : {categorie}",
        "spin_suffix": "",
        "spin_max": 150,
        "spin_val_clean": 60,
        "spin_val_unclean": 10,
    },
    {
        "thresholds": [(85, "Supérieur"), (65, "Standard"), (40, "Minimal")],
        "var": "grade",
        "display": "Grade : {grade}",
        "spin_suffix": " pts",
        "spin_max": 100,
        "spin_val_clean": 70,
        "spin_val_unclean": 25,
    },
]

# Calculs pour div_zero
DIV_ZERO_CALC_SETS = [
    {
        "numerator_label":   "Total",
        "denominator_label": "Nombre",
        "result_label":      "Moyenne",
        "num_var":   "total",
        "denom_var": "count",
        "result_var": "moyenne",
        "code_template": [
            "{num_var} = self.{num_widget}.value",
            "{denom_var} = self.{denom_widget}.value",
            "{result_var} = {num_var} / {denom_var}",
            "self.{display_widget}.text = f'{result_label} : {{{result_var}:.2f}}'",
        ],
    },
    {
        "numerator_label":   "Score total",
        "denominator_label": "Nb étudiants",
        "result_label":      "Moyenne classe",
        "num_var":   "score",
        "denom_var": "nb",
        "result_var": "moyenne",
        "code_template": [
            "{num_var} = self.{num_widget}.value",
            "{denom_var} = self.{denom_widget}.value",
            "{result_var} = {num_var} / {denom_var}",
            "self.{display_widget}.text = f'{result_label} : {{{result_var}:.1f}}'",
        ],
    },
    {
        "numerator_label":   "Distance",
        "denominator_label": "Temps",
        "result_label":      "Vitesse",
        "num_var":   "distance",
        "denom_var": "temps",
        "result_var": "vitesse",
        "code_template": [
            "{num_var} = self.{num_widget}.value",
            "{denom_var} = self.{denom_widget}.value",
            "{result_var} = {num_var} / {denom_var}",
            "self.{display_widget}.text = f'{result_label} : {{{result_var}:.2f}} km/h'",
        ],
    },
    {
        "numerator_label":   "Revenus",
        "denominator_label": "Nb mois",
        "result_label":      "Revenu mensuel",
        "num_var":   "revenus",
        "denom_var": "mois",
        "result_var": "mensuel",
        "code_template": [
            "{num_var} = self.{num_widget}.value",
            "{denom_var} = self.{denom_widget}.value",
            "{result_var} = {num_var} / {denom_var}",
            "self.{display_widget}.text = f'{result_label} : {{{result_var}:.2f}} $'",
        ],
    },
    {
        "numerator_label":   "Points",
        "denominator_label": "Niveaux",
        "result_label":      "Points/niveau",
        "num_var":   "points",
        "denom_var": "niveaux",
        "result_var": "ratio",
        "code_template": [
            "{num_var} = self.{num_widget}.value",
            "{denom_var} = self.{denom_widget}.value",
            "{result_var} = {num_var} / {denom_var}",
            "self.{display_widget}.text = f'{result_label} : {{{result_var}:.1f}}'",
        ],
    },
]

# Boucles pour infinite_loop
LOOP_SETS = [
    {
        "counter_var": "i",
        "limit_var":   "total",
        "limit_label": "Itérations",
        "result_label": "éléments traités",
        "code_clean": [
            "{limit_var} = self.{spin_widget}.value",
            "{counter_var} = 0",
            "while {counter_var} < {limit_var}:",
            "    {counter_var} += 1",
            "self.{display_widget}.text = f'{{{counter_var}}} {result_label}'",
        ],
        "code_unclean": [
            "{limit_var} = self.{spin_widget}.value",
            "{counter_var} = 0",
            "while {counter_var} < {limit_var}:",
            "    self.{display_widget}.text = f'{{{counter_var}}} {result_label}'",
            "self.{display_widget}.text = f'Terminé : {{{limit_var}}} {result_label}'",
        ],
    },
    {
        "counter_var": "n",
        "limit_var":   "max_val",
        "limit_label": "Maximum",
        "result_label": "cycles complétés",
        "code_clean": [
            "{limit_var} = self.{spin_widget}.value",
            "{counter_var} = 0",
            "while {counter_var} < {limit_var}:",
            "    {counter_var} += 1",
            "self.{display_widget}.text = f'{{{counter_var}}} {result_label}'",
        ],
        "code_unclean": [
            "{limit_var} = self.{spin_widget}.value",
            "{counter_var} = 0",
            "step = 1",
            "while {counter_var} < {limit_var}:",
            "    step += 1",
            "self.{display_widget}.text = f'Terminé : {{{counter_var}}} {result_label}'",
        ],
    },
    {
        "counter_var": "k",
        "limit_var":   "cible",
        "limit_label": "Cible",
        "result_label": "opérations",
        "code_clean": [
            "{limit_var} = self.{spin_widget}.value",
            "{counter_var} = 0",
            "while {counter_var} < {limit_var}:",
            "    {counter_var} += 1",
            "self.{display_widget}.text = f'{{{counter_var}}} {result_label}'",
        ],
        "code_unclean": [
            "{limit_var} = self.{spin_widget}.value",
            "{counter_var} = 0",
            "acc = 0",
            "while {counter_var} < {limit_var}:",
            "    acc += {counter_var}",
            "self.{display_widget}.text = f'Résultat : {{acc}}'",
        ],
    },
    {
        "counter_var": "idx",
        "limit_var":   "nb",
        "limit_label": "Nombre",
        "result_label": "tours",
        "code_clean": [
            "{limit_var} = self.{spin_widget}.value",
            "{counter_var} = 0",
            "while {counter_var} < {limit_var}:",
            "    {counter_var} += 1",
            "self.{display_widget}.text = f'Fait : {{{counter_var}}} {result_label}'",
        ],
        "code_unclean": [
            "{limit_var} = self.{spin_widget}.value",
            "{counter_var} = 0",
            "total = 0",
            "while {counter_var} < {limit_var}:",
            "    total = total + 1",
            "self.{display_widget}.text = f'Total : {{total}}'",
        ],
    },
    {
        "counter_var": "pos",
        "limit_var":   "longueur",
        "limit_label": "Longueur",
        "result_label": "pas effectués",
        "code_clean": [
            "{limit_var} = self.{spin_widget}.value",
            "{counter_var} = 0",
            "while {counter_var} < {limit_var}:",
            "    {counter_var} += 1",
            "self.{display_widget}.text = f'{{{counter_var}}} {result_label}'",
        ],
        "code_unclean": [
            "{limit_var} = self.{spin_widget}.value",
            "{counter_var} = 0",
            "delta = 1",
            "while {counter_var} < {limit_var}:",
            "    delta += 1",
            "self.{display_widget}.text = f'{{{counter_var}}} {result_label}'",
        ],
    },
]

# Params dupliqués
DUP_PARAMS_SETS = [
    {
        "signal": "valueChanged",
        "widget_type": "QSlider",
        "extra_props": [
            {"name": "minimum", "type": "int", "value": 0},
            {"name": "maximum", "type": "int", "value": 100},
            {"name": "value",   "type": "int", "value": 50},
        ],
        "param_name": "value",
        "display_code_clean":   "self.{display}.text = f'Valeur : {{value}}'",
        "display_code_unclean": "self.{display}.text = f'Valeur : {{value}}'",
    },
    {
        "signal": "valueChanged",
        "widget_type": "QSpinBox",
        "extra_props": [
            {"name": "minimum", "type": "int", "value": 0},
            {"name": "maximum", "type": "int", "value": 100},
            {"name": "value",   "type": "int", "value": 0},
        ],
        "param_name": "value",
        "display_code_clean":   "self.{display}.text = f'Score : {{value}}'",
        "display_code_unclean": "self.{display}.text = f'Score : {{value}}'",
    },
    {
        "signal": "valueChanged",
        "widget_type": "QSlider",
        "extra_props": [
            {"name": "minimum", "type": "int", "value": 0},
            {"name": "maximum", "type": "int", "value": 360},
            {"name": "value",   "type": "int", "value": 0},
        ],
        "param_name": "value",
        "display_code_clean":   "self.{display}.text = f'Angle : {{value}}°'",
        "display_code_unclean": "self.{display}.text = f'Angle : {{value}}°'",
    },
    {
        "signal": "valueChanged",
        "widget_type": "QSlider",
        "extra_props": [
            {"name": "minimum", "type": "int", "value": 0},
            {"name": "maximum", "type": "int", "value": 255},
            {"name": "value",   "type": "int", "value": 128},
        ],
        "param_name": "value",
        "display_code_clean":   "self.{display}.text = f'Intensité : {{value}}'",
        "display_code_unclean": "self.{display}.text = f'Intensité : {{value}}'",
    },
    {
        "signal": "valueChanged",
        "widget_type": "QSpinBox",
        "extra_props": [
            {"name": "minimum", "type": "int", "value": 1},
            {"name": "maximum", "type": "int", "value": 10},
            {"name": "value",   "type": "int", "value": 5},
            {"name": "prefix",  "type": "str", "value": "Priorité : "},
        ],
        "param_name": "value",
        "display_code_clean":   "self.{display}.text = f'Priorité sélectionnée : {{value}}'",
        "display_code_unclean": "self.{display}.text = f'Priorité sélectionnée : {{value}}'",
    },
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def new_id(counter):
    counter[0] += 1
    return str(counter[0])


def make_project(project_id, project_name, app_type, window_title,
                 components, links):
    return [{
        "id_project":   str(project_id),
        "id_owner":     "1",
        "last_update":  "2026-05-23T10:00:00.000-Z",
        "project_name": project_name,
        "components":   components,
        "links":        links,
    }]


def make_vbox(comp_id, name, children, spacing=10):
    return {
        "id":          comp_id,
        "type":        "QVBoxLayout",
        "category":    "layout",
        "name":        name,
        "variable":    [],
        "inheritance": [],
        "module":      "PySide6.QtWidgets",
        "child":       children,
        "properties":  [{"name": "spacing", "type": "int", "value": spacing}],
        "function":    [],
    }


def make_label(comp_id, name, text):
    return {
        "id":          comp_id,
        "type":        "QLabel",
        "category":    "widget",
        "name":        name,
        "variable":    [],
        "inheritance": [],
        "module":      "PySide6.QtWidgets",
        "child":       [],
        "properties":  [{"name": "text", "type": "str", "value": text}],
        "function":    [],
    }


def make_button(comp_id, name, label, signal_id, signal_name="clicked"):
    return {
        "id":          comp_id,
        "type":        "QPushButton",
        "category":    "widget",
        "name":        name,
        "variable":    [],
        "inheritance": [],
        "module":      "PySide6.QtWidgets",
        "child":       [],
        "properties":  [{"name": "text", "type": "str", "value": label}],
        "function":    [{"id": signal_id, "name": signal_name, "is_intern": True, "code": ""}],
    }


def make_spinbox(comp_id, name, props, signal_id=None, signal_name=None):
    comp = {
        "id":          comp_id,
        "type":        "QSpinBox",
        "category":    "widget",
        "name":        name,
        "variable":    [],
        "inheritance": [],
        "module":      "PySide6.QtWidgets",
        "child":       [],
        "properties":  props,
        "function":    [],
    }
    if signal_id:
        comp["function"] = [{"id": signal_id, "name": signal_name, "is_intern": True, "code": ""}]
    return comp


def make_generic_widget(comp_id, wtype, module, name, props, signal_id=None, signal_name=None):
    comp = {
        "id":          comp_id,
        "type":        wtype,
        "category":    "widget",
        "name":        name,
        "variable":    [],
        "inheritance": [],
        "module":      module,
        "child":       [],
        "properties":  props,
        "function":    [],
    }
    if signal_id:
        comp["function"] = [{"id": signal_id, "name": signal_name, "is_intern": True, "code": ""}]
    return comp


def make_custom(comp_id, app_type, window_title, variables, child_ids, functions):
    return {
        "id":          comp_id,
        "type":        app_type,
        "category":    "custom",
        "name":        "app",
        "module":      "PySide6.QtCore",
        "variable":    variables,
        "inheritance": [{"type": "QWidget", "module": "PySide6.QtWidgets"}],
        "child":       child_ids,
        "properties":  [{"name": "window_title", "type": "str", "value": window_title}],
        "function":    functions,
    }


def make_variable(var_id, name, ref_id=None, val_type="id", val=None, scope="public"):
    if ref_id is not None:
        value = {"type": "id", "value": ref_id}
    else:
        value = {"type": val_type, "value": val}
    return {
        "id":           var_id,
        "name":         name,
        "value":        value,
        "scope":        scope,
        "is_in_the_box": False,
    }


def make_function(func_id, name, params, code):
    return {
        "id":        func_id,
        "name":      name,
        "params":    params,
        "code":      code,
        "is_intern": False,
    }


def make_link(link_id, source, target):
    return {"id": link_id, "source": source, "target": target, "type": "signal_slot"}


def fmt_code(template_lines, **kwargs):
    return [line.format(**kwargs) for line in template_lines]


def save(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# ---------------------------------------------------------------------------
# Générateurs par pattern
# ---------------------------------------------------------------------------

def gen_infinite_loop(idx, loop_set, app_idx, clean):
    c = [0]
    ls = loop_set

    app_type     = APP_NAMES[app_idx % len(APP_NAMES)]
    project_name = PROJECT_NAMES[app_idx % len(PROJECT_NAMES)]
    win_title    = WINDOW_TITLES[app_idx % len(WINDOW_TITLES)]
    btn_label    = BUTTON_LABELS[app_idx % len(BUTTON_LABELS)]

    custom_id  = new_id(c)
    spin_id    = new_id(c)
    display_id = new_id(c)
    btn_id     = new_id(c)
    layout_id  = new_id(c)
    sig_id     = new_id(c)
    func_id    = new_id(c)
    var1_id    = new_id(c)
    var2_id    = new_id(c)
    var3_id    = new_id(c)

    spin_name    = "count_spin"
    display_name = "result_label"
    btn_name     = "run_btn"

    spin_props = [
        {"name": "minimum", "type": "int", "value": 1},
        {"name": "maximum", "type": "int", "value": 50},
        {"name": "value",   "type": "int", "value": 5},
        {"name": "prefix",  "type": "str", "value": f"{ls['limit_label']} : "},
    ]

    code_tpl = ls["code_clean"] if clean else ls["code_unclean"]
    code = fmt_code(code_tpl,
                    limit_var=ls["limit_var"],
                    counter_var=ls["counter_var"],
                    spin_widget=spin_name,
                    display_widget=display_name,
                    result_label=ls["result_label"])

    variables = [
        make_variable(var1_id, spin_name,    ref_id=spin_id),
        make_variable(var2_id, display_name, ref_id=display_id),
        make_variable(var3_id, btn_name,     ref_id=btn_id),
    ]
    functions = [make_function(func_id, "on_run", ["self"], code)]

    custom = make_custom(custom_id, app_type, win_title, variables, [layout_id], functions)
    layout = make_vbox(layout_id, "main_layout", [spin_id, btn_id, display_id])
    spin   = make_spinbox(spin_id, spin_name, spin_props)
    btn    = make_button(btn_id, btn_name, btn_label, sig_id)
    lbl    = make_label(display_id, display_name, "En attente...")

    components = [custom, layout, spin, btn, lbl]
    links      = [make_link("L1", sig_id, func_id)]

    return make_project(idx, project_name, app_type, win_title, components, links)


def gen_div_zero(idx, calc_set, num_widget_cfg, denom_widget_cfg, app_idx, clean):
    c = [0]
    cs = calc_set

    app_type     = APP_NAMES[app_idx % len(APP_NAMES)]
    project_name = PROJECT_NAMES[app_idx % len(PROJECT_NAMES)]
    win_title    = WINDOW_TITLES[app_idx % len(WINDOW_TITLES)]
    btn_label    = BUTTON_LABELS[app_idx % len(BUTTON_LABELS)]

    custom_id  = new_id(c)
    num_id     = new_id(c)
    denom_id   = new_id(c)
    display_id = new_id(c)
    btn_id     = new_id(c)
    layout_id  = new_id(c)
    sig_id     = new_id(c)
    func_id    = new_id(c)

    num_name     = "numerator_spin"
    denom_name   = "denominator_spin"
    display_name = "result_label"
    btn_name     = "calc_btn"

    num_props   = num_widget_cfg["extra_props_clean"]
    if clean:
        denom_props = denom_widget_cfg["extra_props_clean"]
    else:
        denom_props = denom_widget_cfg["extra_props_unclean_divzero"]

    code = fmt_code(cs["code_template"],
                    num_var=cs["num_var"],
                    denom_var=cs["denom_var"],
                    result_var=cs["result_var"],
                    num_widget=num_name,
                    denom_widget=denom_name,
                    display_widget=display_name,
                    result_label=cs["result_label"])

    var_ids = [new_id(c) for _ in range(4)]
    variables = [
        make_variable(var_ids[0], num_name,     ref_id=num_id),
        make_variable(var_ids[1], denom_name,   ref_id=denom_id),
        make_variable(var_ids[2], display_name, ref_id=display_id),
        make_variable(var_ids[3], btn_name,     ref_id=btn_id),
    ]
    functions = [make_function(func_id, "on_calc", ["self"], code)]

    custom  = make_custom(custom_id, app_type, win_title, variables, [layout_id], functions)
    layout  = make_vbox(layout_id, "main_layout", [num_id, denom_id, btn_id, display_id])
    num_w   = make_spinbox(num_id,   num_name,   num_props)
    denom_w = make_spinbox(denom_id, denom_name, denom_props)
    btn     = make_button(btn_id, btn_name, btn_label, sig_id)
    lbl     = make_label(display_id, display_name, "—")

    components = [custom, layout, num_w, denom_w, btn, lbl]
    links      = [make_link("L1", sig_id, func_id)]

    return make_project(idx, project_name, app_type, win_title, components, links)


def gen_undef_var(idx, mention_set, app_idx, clean):
    c = [0]
    ms = mention_set

    app_type     = APP_NAMES[app_idx % len(APP_NAMES)]
    project_name = PROJECT_NAMES[app_idx % len(PROJECT_NAMES)]
    win_title    = WINDOW_TITLES[app_idx % len(WINDOW_TITLES)]
    btn_label    = BUTTON_LABELS[app_idx % len(BUTTON_LABELS)]

    custom_id  = new_id(c)
    spin_id    = new_id(c)
    display_id = new_id(c)
    btn_id     = new_id(c)
    layout_id  = new_id(c)
    sig_id     = new_id(c)
    func_id    = new_id(c)

    spin_name    = "score_spin"
    display_name = "result_label"
    btn_name     = "eval_btn"

    spin_val = ms["spin_val_clean"] if clean else ms["spin_val_unclean"]
    spin_props = [
        {"name": "minimum", "type": "int", "value": 0},
        {"name": "maximum", "type": "int", "value": ms["spin_max"]},
        {"name": "value",   "type": "int", "value": spin_val},
    ]
    if ms["spin_suffix"]:
        spin_props.append({"name": "suffix", "type": "str", "value": ms["spin_suffix"]})

    # Build if/elif chain
    code = ["score = self.score_spin.value"]
    for i, (threshold, label) in enumerate(ms["thresholds"]):
        kw = "if" if i == 0 else "elif"
        code.append(f"{kw} score >= {threshold}:")
        code.append(f"    {ms['var']} = '{label}'")

    if clean:
        code.append("else:")
        code.append(f"    {ms['var']} = 'Insuffisant'")

    display_line = "self." + display_name + ".text = f'" + ms["display"].replace("{", "{{").replace("}", "}}").replace("{{" + ms["var"] + "}}", "{" + ms["var"] + "}") + "'"
    code.append(display_line)

    var_ids = [new_id(c) for _ in range(3)]
    variables = [
        make_variable(var_ids[0], spin_name,    ref_id=spin_id),
        make_variable(var_ids[1], display_name, ref_id=display_id),
        make_variable(var_ids[2], btn_name,     ref_id=btn_id),
    ]
    functions = [make_function(func_id, "on_eval", ["self"], code)]

    custom = make_custom(custom_id, app_type, win_title, variables, [layout_id], functions)
    layout = make_vbox(layout_id, "main_layout", [spin_id, btn_id, display_id])
    spin   = make_spinbox(spin_id, spin_name, spin_props)
    btn    = make_button(btn_id, btn_name, btn_label, sig_id)
    lbl    = make_label(display_id, display_name, "En attente...")

    components = [custom, layout, spin, btn, lbl]
    links      = [make_link("L1", sig_id, func_id)]

    return make_project(idx, project_name, app_type, win_title, components, links)


def gen_dup_params(idx, dup_set, app_idx, clean):
    c = [0]
    ds = dup_set

    app_type     = APP_NAMES[app_idx % len(APP_NAMES)]
    project_name = PROJECT_NAMES[app_idx % len(PROJECT_NAMES)]
    win_title    = WINDOW_TITLES[app_idx % len(WINDOW_TITLES)]

    custom_id  = new_id(c)
    widget_id  = new_id(c)
    display_id = new_id(c)
    layout_id  = new_id(c)
    sig_id     = new_id(c)
    func_id    = new_id(c)

    widget_name  = "input_widget"
    display_name = "value_label"

    display_code = ds["display_code_clean"] if clean else ds["display_code_unclean"]
    display_code = display_code.format(display=display_name)

    if clean:
        params = ["self", ds["param_name"]]
    else:
        params = ["self", ds["param_name"], ds["param_name"]]

    code = [display_code]
    functions = [make_function(func_id, "on_changed", params, code)]

    var_ids = [new_id(c) for _ in range(2)]
    variables = [
        make_variable(var_ids[0], widget_name,  ref_id=widget_id),
        make_variable(var_ids[1], display_name, ref_id=display_id),
    ]

    custom = make_custom(custom_id, app_type, win_title, variables, [layout_id], functions)
    layout = make_vbox(layout_id, "main_layout", [widget_id, display_id])
    widget = make_generic_widget(widget_id, ds["widget_type"], "PySide6.QtWidgets",
                                  widget_name, ds["extra_props"], sig_id, ds["signal"])
    lbl    = make_label(display_id, display_name, "—")

    components = [custom, layout, widget, lbl]
    links      = [make_link("L1", sig_id, func_id)]

    return make_project(idx, project_name, app_type, win_title, components, links)


# ---------------------------------------------------------------------------
# Génération principale
# ---------------------------------------------------------------------------

def main():
    counter = 0

    # --- INFINITE LOOP : 5 loop_sets x 6 app variants = 30 clean + 30 unclean
    for loop_idx, loop_set in enumerate(LOOP_SETS):
        for variant in range(6):
            app_idx = loop_idx * 6 + variant
            counter += 1

            data_clean = gen_infinite_loop(counter, loop_set, app_idx, clean=True)
            save(data_clean, OUT_CLEAN / f"loop_clean_{counter:03d}.json")

            data_unclean = gen_infinite_loop(counter, loop_set, app_idx, clean=False)
            save(data_unclean, OUT_UNCLEAN / f"loop_unclean_{counter:03d}.json")

    # --- DIV ZERO : 5 calc_sets x 3 widget_cfgs x 2 combos = 30 clean + 30 unclean
    div_counter = 0
    for calc_set in DIV_ZERO_CALC_SETS:
        for num_cfg in NUMERIC_WIDGETS:
            for denom_cfg in NUMERIC_WIDGETS[:2]:
                div_counter += 1
                app_idx = div_counter + 100

                data_clean = gen_div_zero(div_counter, calc_set, num_cfg, denom_cfg, app_idx, clean=True)
                save(data_clean, OUT_CLEAN / f"divzero_clean_{div_counter:03d}.json")

                data_unclean = gen_div_zero(div_counter, calc_set, num_cfg, denom_cfg, app_idx, clean=False)
                save(data_unclean, OUT_UNCLEAN / f"divzero_unclean_{div_counter:03d}.json")

    # --- UNDEF VAR : 5 mention_sets x 6 app variants = 30 clean + 30 unclean
    undef_counter = 0
    for mention_set in MENTION_SETS:
        for variant in range(6):
            undef_counter += 1
            app_idx = undef_counter + 200

            data_clean = gen_undef_var(undef_counter, mention_set, app_idx, clean=True)
            save(data_clean, OUT_CLEAN / f"undefvar_clean_{undef_counter:03d}.json")

            data_unclean = gen_undef_var(undef_counter, mention_set, app_idx, clean=False)
            save(data_unclean, OUT_UNCLEAN / f"undefvar_unclean_{undef_counter:03d}.json")

    # --- DUP PARAMS : 5 dup_sets x 6 app variants = 30 clean + 30 unclean
    dup_counter = 0
    for dup_set in DUP_PARAMS_SETS:
        for variant in range(6):
            dup_counter += 1
            app_idx = dup_counter + 300

            data_clean = gen_dup_params(dup_counter, dup_set, app_idx, clean=True)
            save(data_clean, OUT_CLEAN / f"dupparams_clean_{dup_counter:03d}.json")

            data_unclean = gen_dup_params(dup_counter, dup_set, app_idx, clean=False)
            save(data_unclean, OUT_UNCLEAN / f"dupparams_unclean_{dup_counter:03d}.json")

    # Compter
    n_clean   = len(list(OUT_CLEAN.glob("*.json")))
    n_unclean = len(list(OUT_UNCLEAN.glob("*.json")))
    print(f"Généré : {n_clean} clean, {n_unclean} unclean")
    print(f"Total  : {n_clean + n_unclean} fichiers")


if __name__ == "__main__":
    main()
