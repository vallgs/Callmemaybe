import json
from .parsing.arg import argument
from .loader import read_calling_tests, read_function_definition
from .engine import GenerationEngine
from src.llm_sdk.llm_sdk import Small_LLM_Model
from tqdm import tqdm


def main():
    args = argument()
    functions = read_function_definition(args.functions_definition)
    test = read_calling_tests(args.input)

    line = []
    results = []
    for f in functions:
        params_str = ", ".join(f"{name}: {p.type}" for name, p in f.parameters.items())
        line.append(f"{f.name}({params_str}) - {f.description}")
    functions_text = "\n".join(line)
    llm = Small_LLM_Model()
    engine = GenerationEngine(llm, functions)
    for t in tqdm(test, desc="Prompt generation"):
        print(f"\n→ {t.prompt}")
        prompt_text = f"fonctio disponible:\n{functions_text}\n\nQuestion: {t.prompt}\nJSON:"
        token_ids = llm.encode(prompt_text).tolist()[0]
        brace_depth = 0
        seen_open = False
        while True:
            next_id = engine.generate_step(token_ids)
            token_ids.append(next_id)
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
        full_text = llm.decode(token_ids)
        json_text = full_text.split("JSON:")[1]
        print(f"\nJSON generer: {json_text}")
        result = json.loads(json_text)
        result["prompt"] = t.prompt
        results.append(result)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    main()
