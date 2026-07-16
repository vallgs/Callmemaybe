import json
from src.parsing.arg import argument
from .loader import read_calling_tests, read_function_definition
from .engine import GenerationEngine
from llm_sdk import Small_LLM_Model
from tqdm import tqdm
import os


def main() -> None:
    args = argument()
    functions = read_function_definition(args.functions_definition)
    test = read_calling_tests(args.input)

    line = []
    results = []
    for f in functions:
        params_str = ", ".join(f"{name}: {p.type}"
                               for name, p in f.parameters.items())
        line.append(f"{f.name}({params_str}) - {f.description}")
    functions_text = "\n".join(line)
    llm = Small_LLM_Model()
    engine = GenerationEngine(llm, functions)

    for t in tqdm(test, desc="Prompt generation"):
        print(f"\n→ {t.prompt}")
        prompt_text = (
            f"fonction disponible:\n{functions_text}\n\n"
            f"Question: {t.prompt}\nJSON:"
        )
        token_ids = llm.encode(prompt_text).tolist()[0]
        res = {"prompt": t.prompt}
        brace_depth = 0
        seen_open = False
        MAX_TOKENS = 100
        tokens_genere = 0
        while True:
            next_id = engine.generate_step(token_ids)
            token_ids.append(next_id)
            tokens_genere += 1
            generated = llm.decode([next_id])
            print(f"token: '{generated}'", end=" ", flush=True)
            for c in generated:
                if c == '{':
                    brace_depth += 1
                    seen_open = True
                elif c == '}':
                    brace_depth -= 1
            if seen_open and brace_depth == 0:
                break
            if tokens_genere > MAX_TOKENS:
                print("\nLimite de token atteinte")
                break
        full_text = llm.decode(token_ids)
        json_text = full_text.split("JSON:")[1]
        print(f"\nJSON generer: {json_text}")
        try:
            result = json.loads(json_text)
            res.update(result)
            fn = next((f for f in functions if f.name == result["name"]), None)
            if fn is None:
                continue
            for r in result["parameters"]:
                if fn.parameters[r].type == "number":
                    result["parameters"][r] = float(result["parameters"][r])
            results.append(res)
        except json.JSONDecodeError as e:
            print(f"\n JSON error '{t.prompt}': {e}")
    output_folder = os.path.dirname(args.output)
    try:
        os.makedirs(output_folder, 0o777, True)
    except (OSError) as e:
        print(f"{e}")
    try:
        with open(args.output, "w", encoding="utf-8") as a:
            json.dump(results, a, indent=2)
    except (json.JSONDecodeError, OSError) as e:
        print(f"\n JSON error '{t.prompt}': {e}")


if __name__ == "__main__":
    main()
