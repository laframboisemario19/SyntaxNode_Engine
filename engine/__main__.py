import json

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

    # print(engine.available_lang)
    # print(engine.available_lib)
    # print(engine.current_lang)
    # print(engine.current_lib)

if __name__ == "__main__":
    main()