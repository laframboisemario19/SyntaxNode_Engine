"""CODE GÉNÉRÉ PAR CLAUDE POUR TESTER LES SCRIPTS GÉNÉRÉS."""

import json
import zipfile
import io
from pathlib import Path

# Adaptez ce chemin selon votre structure de projet
from .engine import SyntaxNodeEngine
from .engine.strategies import ConfigType

DATASETS_PATH = Path(__file__).parent.parent / "core" / "ai_data" / "datasets" / "syntax_node_error"

def run_validation():
    engine = SyntaxNodeEngine()
    engine.set_language("python")
    engine.set_lib("qt", ConfigType.DEFAULT)

    results = {"ok": [], "error": []}
    all_py_files = {}  # nom_fichier -> contenu .py

    for label, folder in [("clean", DATASETS_PATH / "clean"),
                           ("unclean", DATASETS_PATH / "unclean")]:
        for json_path in sorted(folder.glob("*.json")):
            try:
                with open(json_path, encoding="utf-8") as f:
                    data = json.load(f)

                zip_buffer = engine.get_code_files(data)

                # Extraire le .py du zip retourné
                with zipfile.ZipFile(zip_buffer) as zf:
                    py_code = zf.read("main_application.py").decode("utf-8")

                py_name = f"{label}__{json_path.stem}.py"
                all_py_files[py_name] = py_code
                results["ok"].append(json_path.name)

            except Exception as e:
                results["error"].append((json_path.name, type(e).__name__, str(e)[:120]))

    # Rapport
    print(f"\n✓ {len(results['ok'])} fichiers OK")
    print(f"✗ {len(results['error'])} fichiers en erreur\n")
    for name, etype, msg in results["error"]:
        print(f"  [{etype}] {name}")
        print(f"    {msg}")

    # Zip de tous les .py générés
    if all_py_files:
        out_zip = Path("generated_scripts.zip")
        with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as zf:
            for py_name, py_code in all_py_files.items():
                zf.writestr(py_name, py_code)
        print(f"\nScripts Python sauvegardés dans : {out_zip}")
        print(f"  ({len(all_py_files)} fichiers)")

if __name__ == "__main__":
    run_validation()