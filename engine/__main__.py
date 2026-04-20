import json

from .core import SyntaxNodeEngine, ConfigType

def main():
    ## Instanciation de l'engine
    engine = SyntaxNodeEngine()

    engine.set_language("python")
    engine.set_lib("qt", ConfigType.DEFAULT)

    ## Obtenir les metadata
    meta_objects = engine.get_meta_objects()

    path = "./data/projet_test3.json"
    data = None
    with open(path, encoding="utf-8") as file:
        data = json.load(file)

    ## Obtenir le buffer pour le fichier zip de code
    code_files = engine.get_code_files(data)

    ## Transformer le buffer en fichier .zip
    output_path = f"./data/generated_test.zip"
    with open(output_path, "wb") as out_file:
        out_file.write(code_files.getvalue())

    ## Obtenir le buffer contenant l'image demandée
    bitmap_buffer = engine.generate_bitmap(data, "3")

if __name__ == "__main__":
    main()