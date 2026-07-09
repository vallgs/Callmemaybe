from pydantic import ValidationError
from models import PromptTest, FunctionDefinition
import json


def read_calling_tests(path: str) -> list[PromptTest]:
    validated_tests = []
    try:
        with open(path) as f:
            data = json.load(f)
        for d in data:
            test_object = PromptTest(**d)
            validated_tests.append(test_object)

    except OSError as e:
        print(f"{e}")
    except ValidationError as e:
        print(f"Validation error in the JSON: {e}")
    except json.JSONDecodeError as e:
        print(f"{e}")

    return validated_tests


def read_function_definition(path: str) -> list[FunctionDefinition]:
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
    except json.JSONDecodeError as e:
        print(f"{e}")

    return validated_function
