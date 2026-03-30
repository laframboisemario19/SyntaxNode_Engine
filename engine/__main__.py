import json
import ast

from core import SyntaxNodeEngine, ConfigType

def main():
    engine = SyntaxNodeEngine()

    engine.set_language("python")
    engine.set_lib("qt", ConfigType.TEST)

    meta_objects = engine.get_meta_objects()

    path = "./data/projet_test.json"
    data = None
    with open(path) as file:
        data = json.load(file)
    code_files = engine.get_code_files(data)

    ### Temporairement : ces lignes de code seront dans une classe prochainement
    source_code = ast.unparse(code_files)
    target_line1 = "from __feature__ import true_property, snake_case"
    target_line2 = "from __feature__ import snake_case, true_property"
    modified_line = target_line1 + " #type: ignore[import-not-found]"
    source_code = source_code.replace(target_line1, modified_line)
    modified_line = target_line2 + " #type: ignore[import-not-found]"
    source_code = source_code.replace(target_line2, modified_line)
    output_path = f"./data/generated_test.py"
    with open(output_path, "w", encoding="utf-8") as out_file:
        out_file.write(source_code)
    ##################################################################################

if __name__ == "__main__":
    main()