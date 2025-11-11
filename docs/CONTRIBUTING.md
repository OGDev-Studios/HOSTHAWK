# Contributing to HostHawk

Thank you for your interest in contributing to HostHawk! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and constructive in all interactions with the community.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/hosthawk.git`
3. Create a virtual environment: `python m venv venv`
4. Activate the virtual environment:
    Linux/Mac: `source venv/bin/activate`
    Windows: `venv\Scripts\activate`
5. Install development dependencies: `make installdev`

## Development Workflow

### Setting Up Your Environment

```bash
make installdev
```

### Running Tests

```bash
make test
```

### Code Formatting

We use `black` and `isort` for code formatting:

```bash
make format
```

### Linting

Run linters before submitting:

```bash
make lint
```

## Coding Standards

 Follow PEP 8 style guidelines
 Use type hints for function signatures
 Write docstrings for all public classes and methods
 Keep line length to 100 characters
 Write unit tests for new features
 Ensure all tests pass before submitting

## Commit Messages

 Use clear, descriptive commit messages
 Start with a verb in present tense (e.g., "Add", "Fix", "Update")
 Reference issue numbers when applicable

Example:
```
Add support for IPv6 scanning (#123)

 Implement IPv6 address validation
 Update scanner to handle IPv6 targets
 Add tests for IPv6 functionality
```

## Pull Request Process

1. Create a feature branch: `git checkout b feature/yourfeaturename`
2. Make your changes
3. Run tests and linters
4. Commit your changes
5. Push to your fork
6. Create a Pull Request

### PR Checklist

 [ ] Tests pass locally
 [ ] Code is formatted with black and isort
 [ ] Linters pass (flake8, mypy, pylint)
 [ ] Documentation is updated
 [ ] CHANGELOG.md is updated
 [ ] Commit messages are clear

## Reporting Issues

When reporting issues, please include:

 HostHawk version
 Python version
 Operating system
 Steps to reproduce
 Expected behavior
 Actual behavior
 Error messages or logs

## Feature Requests

We welcome feature requests! Please:

 Check if the feature already exists
 Clearly describe the feature and use case
 Explain why it would be valuable

## Security Issues

Please report security vulnerabilities privately to team@hosthawk.io

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
