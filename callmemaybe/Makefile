install:
	uv sync

run:
	uv run python -m src

debug:
	uv run python -m pdb -m src

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name .venv -exec rm -rf {} +
	@echo "clean ok"

lint:
	-uv run flake8 . --exclude=.venv,src/llm_sdk
	uv run mypy . \
			--warn-return-any \
			--warn-unused-ignores \
			--ignore-missing-imports \
			--disallow-untyped-defs \
			--check-untyped-defs \
			--exclude=.venv \
			--exclude=src/llm_sdk
	@echo "norme ok"

lint_strict:
	-uv run flake8 . --exclude=.venv,src/llm_sdk
	uv run mypy --strict .
	@echo "norme strict ok"