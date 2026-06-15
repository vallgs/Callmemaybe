from pydantic import ValidationError
from models import Parameter, PromptTest, FunctionDefinition
from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def read_calling_tests(path: str) -> list[PromptTest]:
    path = PROJECT_ROOT / "data" / "input" / "function_calling_tests.json"
    validated_tests = []
    try:
        with open(path) as f:
            data = json.load(f)
        for d in data:
            test_object = PromptTest(**d)
            validated_tests.append(test_object)

    except OSError:
        print(f"{e}")
    except ValidationError as e:
        print(f"Validation error in the JSON: {e}")

    return validated_tests


def read_function_definition(path: str) -> list[FunctionDefinition]:
    path = PROJECT_ROOT / "data" / "input" / "function_definition.json"
    validated_function = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for d in data:
            func_object = FunctionDefinition(**d)
            validated_function.append(func_object)
    except OSError as e:
        print(f"{e}")
    except ValidationError as e:
        print(f"{e}")

    return validated_function