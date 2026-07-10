install:
	uv sync
	@echo "finish, you can launch bro"

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
	-uv run flake8 . \
	--exclude=.venv,llm_sdk,moulinette
	uv run mypy src \
			--warn-return-any \
			--warn-unused-ignores \
			--ignore-missing-imports \
			--disallow-untyped-defs \
			--check-untyped-defs \
			--no-namespace-packages
	@echo "norme ok"

lint-strict:
	-uv run flake8 . --exclude=.venv,llm_sdk,moulinette
	uv run mypy --strict src --no-namespace-packages
	@echo "norme strict ok"