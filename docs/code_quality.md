# Python Project Setup and Development Guide

## Table of Contents
1. [Initial Setup](#initial-setup)
2. [Project Structure](#project-structure)
3. [Poetry Package Management](#poetry-package-management)
4. [Pre-commit Configuration](#pre-commit-configuration)
5. [Manual Code Quality Checks](#manual-code-quality-checks)
6. [Common Tasks](#common-tasks)
7. [Troubleshooting](#troubleshooting)

## Initial Setup

### Prerequisites
```bash
# Install Python 3.13
pyenv install 3.13.0a4  # or latest alpha/beta version

# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Set Python version for the project
pyenv local 3.13.0a4
```

### Project Initialization
```bash
# Create new project
poetry new --src your-project-name
cd your-project-name

# Initialize git
git init

# Install dependencies
poetry install

# Setup pre-commit
poetry run pre-commit install
```

## Project Structure
```
your-project/
├── pyproject.toml          # Project & tool configurations
├── .pre-commit-config.yaml # Pre-commit hook configurations
├── src/
│   └── your_package/
│       ├── __init__.py
│       └── your_modules.py
├── tests/
│   ├── __init__.py
│   └── test_your_modules.py
└── .gitignore
```

## Poetry Package Management

### Daily Operations
```bash
# Add new project dependency
poetry add package-name

# Add development dependency
poetry add --group dev package-name

# Update all dependencies
poetry update

# Update specific package
poetry update package-name

# Show outdated packages
poetry show --outdated

# Export requirements.txt (if needed)
poetry export -f requirements.txt --output requirements.txt
poetry export -f requirements.txt --output requirements-dev.txt --with dev
```

### Environment Management
```bash
# Activate virtual environment
poetry shell

# Run command in virtual environment without activation
poetry run python script.py

# Show environment information
poetry env info

# List all environments
poetry env list

# Remove environment
poetry env remove python
```

### Dependency Groups Management
```bash
# Install all dependencies (including dev)
poetry install

# Install only production dependencies
poetry install --without dev

# Update lock file
poetry lock --no-update

# Show dependency tree
poetry show --tree
```

## Pre-commit Configuration

### Installation and Setup
```bash
# Install pre-commit in project
poetry add --group dev pre-commit

# Install pre-commit hooks
poetry run pre-commit install

# Install pre-commit hooks for commit messages (optional)
poetry run pre-commit install --hook-type commit-msg

# Update pre-commit hooks
poetry run pre-commit autoupdate
```

### Manual Runs
```bash
# Run all pre-commit hooks
poetry run pre-commit run --all-files

# Run specific hook
poetry run pre-commit run autopep8 --all-files
poetry run pre-commit run ruff --all-files
poetry run pre-commit run mypy --all-files

# Run hooks on specific files
poetry run pre-commit run --files src/your_package/specific_file.py
```

## Manual Code Quality Checks

### Code Formatting (autopep8)
```bash
# Format single file
poetry run autopep8 --in-place --aggressive --aggressive --aggressive src/your_package/file.py

# Format entire project
poetry run autopep8 --in-place --aggressive --aggressive --aggressive --recursive src/

# Format with specific rules
poetry run autopep8 --in-place --select E,W,F --max-line-length=88 src/
```

### Linting (Ruff)
```bash
# Run linter
poetry run ruff check src/

# Run with automatic fixes
poetry run ruff check --fix src/

# Check specific file
poetry run ruff check src/your_package/file.py

# Show error explanations
poetry run ruff check --show-source src/
```

### Type Checking (MyPy)
```bash
# Run type checker
poetry run mypy src/

# Run with specific flags
poetry run mypy --strict src/

# Check single file
poetry run mypy src/your_package/file.py
```

### Security Checks (Bandit)
```bash
# Run security checks
poetry run bandit -r src/

# Run with specific severity
poetry run bandit -r -ll src/  # Only high severity issues
```

## Common Tasks

### Testing
```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src

# Run specific test file
poetry run pytest tests/test_specific.py

# Run tests matching pattern
poetry run pytest -k "test_pattern"
```

### Code Coverage
```bash
# Generate coverage report
poetry run pytest --cov=src --cov-report=html

# Show coverage in terminal
poetry run pytest --cov=src --cov-report=term-missing
```

### Building Package
```bash
# Build package
poetry build

# Build wheel only
poetry build -f wheel
```

## Troubleshooting

### Common Issues

1. **Import Issues**
```bash
# Add src to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Or run with python path
PYTHONPATH=src poetry run pytest
```

2. **Pre-commit Hook Failed**
```bash
# Skip specific hook temporarily
SKIP=autopep8 git commit -m "message"

# Skip all hooks temporarily
git commit -m "message" --no-verify
```

3. **Poetry Lock Conflicts**
```bash
# Reset lock file
poetry lock --no-update

# Force update
poetry update --lock
```

4. **Virtual Environment Issues**
```bash
# Remove and recreate environment
poetry env remove python
poetry install

# Clear cache
poetry cache clear . --all
```

### Best Practices

1. **Before Committing**
```bash
# Run all checks
poetry run pre-commit run --all-files
poetry run pytest
```

2. **After Pulling Changes**
```bash
# Update dependencies and hooks
poetry install
poetry run pre-commit autoupdate
```

3. **Regular Maintenance**
```bash
# Check for outdated packages
poetry show --outdated

# Update development tools
poetry update pre-commit ruff mypy autopep8 bandit

# Clean up cache
poetry cache clear . --all
```
