from engine import SyntaxNodeEngine
from strat import *

def main():
    engine = SyntaxNodeEngine()

    engine.add_lang_strategy(PythonStrategy())
    engine.add_lib_strategy(QtStrategy())

    engine.set_language("python")
    engine.set_lib("qt")

    meta_objects = engine.get_meta_objects()

    # print(engine.available_lang)
    # print(engine.available_lib)
    # print(engine.current_lang)
    # print(engine.current_lib)

    

if __name__ == "__main__":
    main()