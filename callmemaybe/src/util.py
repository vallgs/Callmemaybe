from models import FunctionDefinition, Parameter


def is_valide(current_text: str, candidate_token: str,
              function: list[FunctionDefinition]) -> bool:
    sequence = current_text + candidate_token

    if len(sequence) == 1 and sequence != "{":
        return False

    if '"name": "' in sequence:
        prefix = sequence.split('"name": "')[1]
        return any(f.name.startswith(prefix) for f in function)
    
    if 

    return True


def get_allowed_tokens_for_parameter(
        param_model: Parameter, current_text: str):
    if param_model.type == "number":
        return ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."]
    return [...]
