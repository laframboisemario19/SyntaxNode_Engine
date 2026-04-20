import zipfile
import ast
from io import BytesIO

class CodeGenerator():
    @classmethod
    def generate_code(cls, tree) -> str:
        code = ast.unparse(tree)
        return cls._add_features(code)

    @staticmethod
    def generate_file(file_name:str, code:str) -> tuple[str, str]:
        return (file_name, code)

    ## Source : https://blog.finxter.com/5-best-ways-to-write-bytes-to-a-zip-file-using-python/    @staticmethod
    def generate_zip_files(files: tuple[tuple[str, str]]) -> BytesIO:
        buffer = BytesIO()
        with zipfile.ZipFile(buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file: 
            for f in files:
                name, data = f
                zip_file.writestr(name, data)
        
        buffer.seek(0)
        return buffer

    @classmethod
    def _add_features(cls, code:str) -> str:
        return cls._snakecase_and_trueproperty(code)

    @staticmethod
    def _snakecase_and_trueproperty(code:str) -> str:
        target_line1 = "from __feature__ import true_property, snake_case"
        target_line2 = "from __feature__ import snake_case, true_property"

        modified_line = target_line1 + " #type: ignore[import-not-found]"
        source_code = code.replace(target_line1, modified_line)
        modified_line = target_line2 + " #type: ignore[import-not-found]"
        source_code = source_code.replace(target_line2, modified_line)

        return source_code
            
        
