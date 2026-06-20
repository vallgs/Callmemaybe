from .models import FunctionDefinition, Parameter


def is_valide(current_text: str, candidate_token: str,
              function: list[FunctionDefinition]) -> bool:
    # on construit le texte complet si on ajoute ce token
    sequence = current_text + candidate_token

    # ETAT 1 : le JSON n'a pas encore commencé, seul "{" est valide
    if "{" not in sequence:
        return False

    # ETAT 2 : "{" est là mais "name": " pas encore → on construit vers {"name": "
    if "{" in sequence and '"name": "' not in sequence:
        waiting = '{"name": "'
        # vérifie que sequence est un préfixe valide de la chaîne attendue
        return waiting.startswith(sequence)

    if '"name": "' in sequence:
        # tout ce qui vient après "name": " dans le texte généré
        prefix = sequence.split('"name": "')[1]
        if '"' in prefix:
            # le nom de fonction est fermé (guillemet présent)
            # on prend tout depuis le guillemet fermant du nom
            continued = '"' + prefix.split('"', 1)[1]
            # ETAT 3 : le nom est fermé mais "parameters": { pas encore là
            if '"parameters": {' not in sequence:
                waiting = '", "parameters": {'
                return waiting.startswith(continued)
            # ETAT 4 : on est dans les paramètres
            if '"parameters":' in sequence:
                # texte après "parameters":
                params_text = sequence.split('"parameters":', 1)[1]
                # si le dernier " est après le dernier : → on écrit un nom de paramètre
                # cherche la position du dernier guillemet dans la section paramètres
                last_quote_pos = params_text.rfind('"')
                # pas encore de guillemet → début des paramètres, on écrit la première clé
                if last_quote_pos == -1:
                    # extraire le nom de la fonction choisie
                    name_fn = sequence.split('"name": "')[1].split('"', 1)[0]
                    # trouver l'objet FunctionDefinition correspondant
                    fn = next((f for f in function if f.name == name_fn), None)
                    if fn is None:
                        return False
                    # le préfixe du paramètre en cours = dernier fragment après "
                    params_prefix = params_text.split('"')[-1]
                    # vérifier que ce préfixe correspond à un paramètre valide
                    return any(p.startswith(params_prefix)
                               for p in fn.parameters)
                else:
                    # extrait tout ce qui précède le dernier guillemet (sans espaces)
                    behind = params_text[:last_quote_pos].rstrip()
                    # si le caractère avant le dernier " est ":" → on écrit une valeur string
                    if behind and behind[-1] == ':':
                        name_fn = sequence.split('"name": "')[1].split('"', 1)[0]
                        fn = next((f for f in function
                                   if f.name == name_fn), None)
                        if fn is None:
                            return False
                        # avant-dernier fragment entre guillemets = nom du paramètre courant
                        params_prefix = params_text.split('"')[-2]
                        return is_token_allowed_by_type(
                            fn.parameters[params_prefix].type, candidate_token)
                    # sinon le dernier " ouvre une clé → on écrit un nom de paramètre
                    else:
                        name_fn = sequence.split('"name": "')[1].split('"', 1)[0]
                        fn = next((f for f in function
                                   if f.name == name_fn), None)
                        if fn is None:
                            return False
                        # dernier fragment après " = préfixe du nom de paramètre en cours
                        params_prefix = params_text.split('"')[-1]
                        return any(p.startswith(params_prefix)
                                   for p in fn.parameters)

        else:
            # ETAT 3 (nom en cours) : vérifier que le token continue un nom valide
            return any(f.name.startswith(prefix) for f in function)

    return True


def get_allowed_tokens_for_parameter(
        param_model: Parameter, current_text: str):
    if param_model.type == "number":
        return ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."]
    return [...]


def is_token_allowed_by_type(param_type: str, candidate_token: str) -> bool:
    if param_type == "number":
        return candidate_token.isdigit() or candidate_token == "-"
    if param_type == "string":
        return candidate_token != '"'
    return True
