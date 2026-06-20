import json
from .parsing.arg import argument
from .loader import read_calling_tests, read_function_definition
from .engine import GenerationEngine
from src.llm_sdk.llm_sdk import Small_LLM_Model


def main():
    args = argument()
    functions = read_function_definition(args.functions_definition)
    test = read_calling_tests(args.input)
    print(test)
    print(functions)
    line = []
    results = []
    for f in functions:
        params_str = ", ".join(f"{name}: {p.type}" for name, p in f.parameters.items())
        line.append(f"{f.name}({params_str}) - {f.description}")
    functions_text = "\n".join(line)
    llm = Small_LLM_Model()
    engine = GenerationEngine(llm, functions)
    for t in test:
        prompt_text = f"fonctio disponible:\n{functions_text}\n\nQuestion: {t.prompt}\nJSON:"
        token_ids = llm.encode(prompt_text).tolist()[0]
        while True:
            next_id = engine.generate_step(token_ids)
            token_ids.append(next_id)
            if llm.decode([next_id]) == "}":
                break
        full_text = llm.decode(token_ids)
        json_text = full_text.split("JSON:")[1]
        result = json.loads(json_text)
        result["prompt"] = t.prompt
        results.append(result)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    main()
