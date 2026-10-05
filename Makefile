.PHONY: setup unit contract all integration cov clean

setup:
	git submodule update --init --recursive
	pip install -r requirements-qa.txt

unit:
	pytest -m "unit"

contract:
	pytest -m "contract"

all:
	pytest -m "unit or contract"

cov:
	pytest -m "unit or contract" --cov=app/src/calculator --cov-report=term-missing

# Butuh IKU_APP_PYTHON (venv aplikasi dengan torch/chromadb/bge-m3) + vector DB.
integration:
	pytest -m "integration"

clean:
	rm -rf .pytest_cache .coverage **/__pycache__
