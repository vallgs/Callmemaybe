*This project has been created as part of the 42 curriculum by vallangl.*

# CallMeMaybe

## Description

CallMeMaybe is a from-scratch implementation of **constrained decoding for function calling** with a small local LLM ([`Qwen/Qwen3-0.6B`](https://huggingface.co/Qwen/Qwen3-0.6B) by default). Given a natural-language question (e.g. *"What is the sum of 2 and 3?"*), the goal is not to make the model answer directly, but to make it output a structurally valid function call: the right function name and correctly typed arguments (e.g. `{"name": "fn_add_numbers", "parameters": {"a": 2.0, "b": 3.0}}`).

Instead of asking the model to "please output valid JSON" and hoping for the best, the token generation loop itself masks out every token that would break the expected JSON grammar, so the model is *structurally* unable to produce an invalid function call.

## Instructions

Requires Python >= 3.10 and [`uv`](https://docs.astral.sh/uv/).

```bash
make install   # uv sync
make run       # uv run python -m src
make debug     # same, under pdb
make lint      # flake8 + mypy
make clean     # remove __pycache__ / .mypy_cache / .venv
```

Custom input/output paths can be passed directly:

```bash
uv run python -m src \
  --input data/input/function_calling_tests.json \
  --functions_definition data/input/functions_definition.json \
  --output data/output/function_calling_results.json
```

## Project structure

```
src/
├── __main__.py            # CLI entrypoint: loads data, runs the generation loop, writes results
├── engine.py               # GenerationEngine: orchestrates logits -> mask -> arg-max per step
├── util.py                 # Grammar/state-machine validator driving the token mask
├── models.py                # Pydantic models: FunctionDefinition, Parameter, PromptTest
├── loader.py                 # JSON loading & validation for functions/tests
└── parsing/arg.py              # CLI argument parsing (--input, --output, --functions_definition)

llm_sdk/                    # Provided package (installed as a local editable dependency)
└── llm_sdk/__init__.py      # Small_LLM_Model: encode/decode/get_logits_from_input_ids/vocab helpers

data/
├── input/
│   ├── functions_definition.json    # Available functions (schema)
│   └── function_calling_tests.json  # Natural-language prompts to translate into calls
└── output/
    └── function_calling_results.json # Generated function calls
```

## Algorithm explanation

For every prompt, generation happens **token by token**. At each step:

1. The model produces raw logits for the next token.
2. A hand-written grammar validator ([`src/util.py`](src/util.py)) checks, for every token in the vocabulary, whether appending it to the text generated so far still leads to a valid `{"name": "...", "parameters": {...}}` object matching one of the known function signatures.
3. Invalid tokens are masked to `-inf` before picking the arg-max token.
4. Generation stops as soon as a balanced, complete JSON object has been produced (or after a token budget is exhausted).
5. The resulting object is parsed, numeric parameters are cast to `float`, and results are written to the output file.

The grammar validator is a small state machine that tracks, character by character, where we are in the JSON structure: the function name, the `"parameters": {` opening, each key (constrained to the target function's known parameter names), the `:` separator, string vs. number values, and the closing braces — always leaving only `,` or `}` open once every required parameter has been written.

## Design decisions

- **Character-level masking rather than token-level grammar rules**: instead of pre-computing which whole tokens are valid per grammar state, `is_valide` re-validates the current text plus each candidate token character by character. This is simpler to reason about and keeps the grammar in one place (`util.py`), at the cost of re-scanning the tail of the string on every candidate token.
- **Pydantic models** (`FunctionDefinition`, `Parameter`, `PromptTest`) are used to validate both input files as soon as they are loaded, so malformed input data fails fast with a clear error instead of propagating `KeyError`s deeper in the pipeline.
- **`GenerationEngine`** is kept separate from the CLI (`__main__.py`): it only knows about logits, masks and token ids, which makes the masking logic testable independently of the model and of file I/O.

## Performance analysis

- **Reliability**: because every generated token is masked against the grammar, the produced JSON is always syntactically valid and schema-compliant — there is no "the model went off script" failure mode.
- **Speed**: masking requires decoding every token in the vocabulary at each generation step to check validity, which is the main performance cost of this approach compared to unconstrained generation.
- **Model size**: Qwen3-0.6B has ~600M parameters and would be unreliable at producing correct JSON on its own; constrained decoding removes that unreliability entirely, at the cost of extra computation per step.

## Challenges faced

- Designing the state machine in `util.py` so that it stays correct when the *candidate* token is only a few characters and can straddle two states (e.g. finishing a key name and opening the `:` separator in the same token) required extracting the "already validated" part of the text (`current_text`) from the part still being proposed (`candidate_token`), and validating the candidate one character at a time (`_valide_params`/`_char_ok`) rather than re-deriving global state from scratch on every call.
- Distinguishing between quotes that open a value/key and quotes that close one (to know whether we're "inside" or "between" fields) needed careful counting of quote parity rather than simple string search.

## Testing strategy

The implementation was validated manually against `data/input/function_calling_tests.json`, checking that:

- every prompt produces valid, parseable JSON in `data/output/function_calling_results.json`;
- the selected function name and parameter types match `functions_definition.json`;
- edge cases (numeric vs. string parameters, functions with multiple parameters) are handled correctly by the state machine in `util.py`.

## Example usage

```bash
$ uv run python -m src
→ What is the sum of 2 and 3?
...
```

Output (`data/output/function_calling_results.json`):

```json
[
  {
    "prompt": "What is the sum of 2 and 3?",
    "name": "fn_add_numbers",
    "parameters": { "a": 2.0, "b": 3.0 }
  }
]
```

## Resources

- [Qwen3 model card](https://huggingface.co/Qwen/Qwen3-0.6B)
- [Hugging Face Transformers documentation](https://huggingface.co/docs/transformers)
- [OpenAI function calling guide](https://platform.openai.com/docs/guides/function-calling)
- [Pydantic documentation](https://docs.pydantic.dev/)

**AI usage**: An AI assistant (Claude) was used to help translate French code comments and docstrings into English, and to review the project's compliance against the subject requirements. All generation logic, the grammar/state-machine validator, and the overall architecture were designed and written by the author; AI-generated suggestions were reviewed and understood before being kept.
