from .models import FunctionDefinition, Parameter


def is_valide(current_text: str, candidate_token: str,
              function: list[FunctionDefinition]) -> bool:
    if "JSON:" in current_text:
        current_text = current_text.split("JSON:")[-1]
    seq = current_text + candidate_token

    # ETAT 1 : construire {"name": "
    if '{"name": "' not in seq:
        return '{"name": "'.startswith(seq.lstrip())

    after_name = seq.split('{"name": "', 1)[1]

    # ETAT 2 : écrire le nom de la fonction
    if '"' not in after_name:
        return any(f.name.startswith(after_name) for f in function)

    fn_name = after_name.split('"', 1)[0]
    fn = next((f for f in function if f.name == fn_name), None)
    if fn is None:
        return False

    # ETAT 3 : construire ", "parameters": {
    rest_seq = '"' + after_name.split('"', 1)[1]
    if '", "parameters": {' not in rest_seq:
        return '", "parameters": {'.startswith(rest_seq)

    # ETAT 4 : extraire inner depuis current_text SEULEMENT (pas seq)
    # pour éviter le double-comptage du candidate dans _valide_params
    params_raw = _params_depuis(current_text, fn_name)

    if params_raw is None:
        # current_text n'a pas encore la section params
        # le candidate complète la transition (déjà validé via seq ci-dessus)
        return True

    # Params déjà fermé → seul } pour l'objet extérieur
    if params_raw.count('{') > 0 and params_raw.count('{') == params_raw.count('}'):
        written = [p for p in fn.parameters if f'"{p}"' in params_raw]
        if len(written) < len(fn.parameters):
            return False
        return all(c in '} ' for c in candidate_token) and '}' in candidate_token

    # { d'ouverture pas encore écrit → le candidate doit le fournir
    brace = params_raw.find('{')
    if brace == -1:
        return '{' in candidate_token or not candidate_token.strip()

    inner = params_raw[brace + 1:]

    # Valider le candidate caractère par caractère contre l'état courant
    return _valide_params(inner, candidate_token, fn)


def _params_depuis(text: str, fn_name: str) -> str | None:
    """Extraire la section params depuis text, ou None si pas encore présente."""
    marker = f'{{"name": "{fn_name}"'
    if marker not in text:
        return None
    after = text.split(marker, 1)[1]
    sep = '", "parameters":'
    rest = '"' + after
    if sep not in rest:
        return None
    return rest.split(sep, 1)[1]


def _valide_params(inner: str, candidate: str, fn: FunctionDefinition) -> bool:
    """Valide le candidate caractère par caractère pour éviter les sauts d'états."""
    current = inner
    for char in candidate:
        if not _char_ok(current, char, fn):
            return False
        current += char
    return True


def _char_ok(inner: str, char: str, fn: FunctionDefinition) -> bool:
    """Vérifie si char est valide comme prochain caractère dans les params."""
    last_q = inner.rfind('"')

    if last_q == -1:
        # Aucun guillemet → attendre " ou espace
        return char in ('"', ' ')

    before = inner[:last_q]
    after = inner[last_q + 1:]
    n_before = before.count('"')

    if n_before % 2 == 0:
        # Dernier " est OUVRANT
        if before.rstrip().endswith(':'):
            # À l'intérieur d'une valeur string : tout caractère est valide
            return True
        else:
            # À l'intérieur d'un nom de clé
            if char == '"':
                return after in fn.parameters  # fermer seulement si clé complète
            return any(k.startswith(after + char) for k in fn.parameters)
    else:
        # Dernier " est FERMANT
        prev_q = inner.rfind('"', 0, last_q)
        closed = inner[prev_q + 1:last_q] if prev_q != -1 else ''
        before_pair = (inner[:prev_q] if prev_q != -1 else '').rstrip()
        after_close = after

        if before_pair.endswith(':'):
            # Vient de fermer une valeur STRING → , ou }
            written = [p for p in fn.parameters if f'"{p}"' in inner]
            if char == '}':
                return len(written) >= len(fn.parameters)
            if char == ',':
                return len(written) < len(fn.parameters)
            return char == ' '
        else:
            # Vient de fermer un nom de CLÉ → attendre : puis valeur
            key = closed
            if key not in fn.parameters:
                return False
            ptype = fn.parameters[key].type

            after_colon = after_close.lstrip()
            if not after_colon:
                return char in (':', ' ')
            if after_colon[0] != ':':
                return False

            value_str = after_colon[1:].lstrip()
            v = value_str.strip()

            if not v:
                # Juste après : → début de valeur
                if ptype == 'number':
                    return char.isdigit() or char in ('-', ' ')
                return char in ('"', ' ')

            if ptype == 'number':
                if ',' in v:
                    # Virgule déjà écrite → prochain param
                    return char in ('"', ' ')
                if '.' in v:
                    after_dot = v.split('.', 1)[1]
                    if after_dot:
                        return _char_terminate(char, inner, fn)
                    return char.isdigit()
                digit_count = sum(c.isdigit() for c in v)
                if digit_count >= 3:
                    return _char_terminate(char, inner, fn)
                return char.isdigit() or char == '.' or _char_terminate(char, inner, fn)

            # string : ne devrait pas arriver (géré par la branche "ouvrant")
            return char in ('"', ' ')


def _char_terminate(char: str, inner: str, fn: FunctionDefinition) -> bool:
    """Vérifie si char peut terminer une valeur numérique."""
    written = [p for p in fn.parameters if f'"{p}"' in inner]
    if char == '}':
        return len(written) >= len(fn.parameters)
    if char == ',':
        return len(written) < len(fn.parameters)
    return char == ' '


def get_allowed_tokens_for_parameter(
        param_model: Parameter, _current_text: str) -> list[str]:
    if param_model.type == "number":
        return ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."]
    return []
