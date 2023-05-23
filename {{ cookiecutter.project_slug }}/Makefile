include .env
export

lint:
	mypy .
	black . --check
	flake8 .
	isort . --check-only

format:
	autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place . --exclude=__init__.py
	isort .
	black .
	flake8 .
	find . -type f -name "*.py" -print0 | xargs -0 add-trailing-comma --py36-plus

test:
	@pytest --cov=src --cov-report=term-missing tests "${@}"

migrate:
	@docker exec backend bash -c "cd / && alembic upgrade head"
