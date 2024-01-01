.PHONY: lint format ci test

lint:
	rye run flake8 .

format:
	rye run black .

test:
	rye run python -m pytest -vv

ci: test
	rye run flake8 .
	rye run black --check .

run:
	rye run python src/main.py

ci-container:
	docker compose exec ai-counselor bash -c "cd / && flake8 src/ tests/"
	docker compose exec ai-counselor bash -c "cd / && black --check src/ tests/"
	docker compose exec ai-counselor bash -c "cd / && pytest -vv src/ tests/"
