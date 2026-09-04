# Contributing to Teddy AI

Thank you for your interest in contributing to Teddy AI!

## Getting Started

1. Read the documentation in `docs/`
2. Understand the architecture in [ARCHITECTURE.md](docs/ARCHITECTURE.md)
3. Review the design decisions in [DECISIONS.md](docs/DECISIONS.md)
4. Follow the setup guide in [SETUP.md](docs/SETUP.md)

## Development Workflow

1. Create a feature branch
2. Make your changes following the code style
3. Add tests for new features
4. Update documentation
5. Submit a pull request

## Code Style

- Use Python 3.9+ type hints
- Follow PEP 8 conventions
- Format code with `black`
- Check with `flake8`
- Run `mypy` for type checking

```bash
black backend/ ai/ voice/ memory/ personality/
flake8 backend/ ai/ voice/ memory/ personality/
mypy backend/ ai/ voice/ memory/ personality/
```

## Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov

# Run specific test file
pytest tests/test_memory.py
```

## Documentation

- Update relevant `.md` files in `docs/`
- Add docstrings to new functions and classes
- Include examples for new features
- Keep README.md current

## Architecture Principles

Remember the core principles:

1. **Modular** - Components must be replaceable
2. **Local-First** - Process locally by default
3. **Hardware-Independent** - Work across devices
4. **Model-Agnostic** - Support multiple LLMs

When adding new features, ensure they follow these principles.

## Reporting Issues

Include:
- Clear description of the issue
- Steps to reproduce
- Expected behavior
- Actual behavior
- System information (OS, Python version, etc.)

## Questions?

- Check existing issues and discussions
- Review the documentation
- Create a discussion thread

Thank you! 🧸
