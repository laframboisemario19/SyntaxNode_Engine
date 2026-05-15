import json
import traceback
from PIL import Image
from io import BytesIO

from .core import SyntaxNodeEngine, ConfigType
from .error import SyntaxNodeError

def main():
    ## Instanciation de l'engine
    engine = SyntaxNodeEngine()

    engine.set_language("python")
    engine.set_lib("qt", ConfigType.DEFAULT)

    # # ## Obtenir les metadata
    # meta_objects = engine.get_meta_objects()

    path = "./core/data/projet_test1.json"
    data = None
    with open(path, encoding="utf-8") as file:
        data = json.load(file)

    engine.validate_data(data)

    path = "./core/data/projet_test1_malsain.json"
    data2 = None
    with open(path, encoding="utf-8") as file:
        data2 = json.load(file)

    ## Obtenir le buffer pour le fichier zip de code
    code_files = engine.get_code_files(data)

    ## Transformer le buffer en fichier .zip
    output_path = f"./core/data/generated_test.zip"
    with open(output_path, "wb") as out_file:
        out_file.write(code_files.getvalue())

    # Obtenir le buffer contenant l'image demandée
    bitmap_buffer = engine.generate_bitmap(data, "3")
    debug(bitmap_buffer)

    engine.train_ai((data, data2))

def debug(bitmap_buffer:BytesIO):
    bitmap_buffer.seek(0)
    img = Image.open(bitmap_buffer)
    img.save("./core/data/debug_output.png")
    

if __name__ == "__main__":
    try:
        main()
    except SyntaxNodeError as e:
        print(e)
