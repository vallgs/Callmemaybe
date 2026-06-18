from models import FunctionDefinition, Parameter


def is_valide(current_text: str, candidate_token: str,
              function: list[FunctionDefinition]) -> bool:
    sequence = current_text + candidate_token
    after = current_text.split('"name": "')[1]

    if len(sequence) == 0 and sequence != "{":
        return False

    if not after:
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


def is_token_allowed_by_type(param_type: str, candidate_token: str) -> bool:
    if param_type == "integer":
        return candidate_token.isdigit() or candidate_token == "-"
    if param_type == "string":
        return candidate_token != '"'
    return True
