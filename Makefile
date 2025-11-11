.PHONY: help install lint format clean run

help:
	@echo "HostHawk - Enterprise Network Scanner"
	@echo ""
	@echo "Available commands:"
	@echo "  make install      - Install production dependencies"
	@echo "  make lint         - Run linters (flake8, black)"
	@echo "  make format       - Format code with black"
	@echo "  make clean        - Clean build artifacts"
	@echo "  make run          - Run the web interface"

install:
	pip install -e .

lint:
	flake8 scanner/ --max-line-length=100 --extend-ignore=E203,W503
	black --check scanner/ web/

format:
	black scanner/ web/ --line-length=100

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

run:
	python -m web.app
