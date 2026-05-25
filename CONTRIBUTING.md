# Contributing to VALDPY

Thank you for your interest in contributing to VALDPY! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and professional in all interactions
- Provide constructive feedback
- Focus on the issue, not the person

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/Valdpy.git`
3. Create a virtual environment: `python -m venv venv`
4. Activate it: `source venv/bin/activate` (or `venv\Scripts\activate` on Windows)
5. Install development dependencies: `pip install -e ".[dev]"`

## Development Workflow

### Before You Start
- Check [Issues](https://github.com/dgaytanjenkins/Valdpy/issues) to see if someone is already working on it
- Create an issue to discuss major changes before starting

### Making Changes

1. Create a feature branch: `git checkout -b feature/your-feature-name`
2. Make your changes following the code style guidelines below
3. Add tests for new functionality
4. Update documentation as needed
5. Ensure all tests pass: `pytest`

### Code Style

This project uses:
- **Black** for code formatting (line length: 100)
- **isort** for import ordering
- **MyPy** for type hints (where practical)
- **Flake8** for linting

Format your code before committing:
```bash
black valdpy/
isort valdpy/
flake8 valdpy/
```

### Type Hints

Use type hints for function signatures:

```python
def get_tests(
    self,
    date: str | datetime,
    profile_id: Optional[str] = None
) -> pd.DataFrame:
    """Get tests from a specific date."""
    pass
```

### Docstring Style

Use NumPy docstring format:

```python
def my_function(param1: str, param2: int) -> bool:
    """
    Short description.
    
    Longer description with more details about what
    the function does and how to use it.
    
    Parameters
    ----------
    param1 : str
        Description of param1
    param2 : int
        Description of param2
        
    Returns
    -------
    bool
        Description of return value
        
    Raises
    ------
    ValueError
        Description of when this is raised
        
    Examples
    --------
    >>> result = my_function("hello", 42)
    >>> result
    True
    """
    pass
```

## Testing

### Write Tests
```python
# tests/test_auth.py
import pytest
from valdpy import ValdAuth

def test_auth_initialization():
    auth = ValdAuth("client_id", "client_secret")
    assert auth.client_id == "client_id"

def test_invalid_region():
    with pytest.raises(ValueError):
        ValdAuth("id", "secret", region="Invalid")
```

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=valdpy

# Run specific test file
pytest tests/test_auth.py

# Run specific test
pytest tests/test_auth.py::test_auth_initialization
```

## Commit Messages

Use clear, descriptive commit messages:

```
Add: New feature description
Fix: Bug fix description
Refactor: Code refactoring description
Docs: Documentation update description
Tests: Test update description

[OPTIONAL: Longer description explaining why this change
was necessary, what problem it solves, etc.]
```

Example:
```
Add: ForceFrame API data pagination support

Implements automatic pagination for ForceFrame API
to handle datasets larger than the single request limit.
Adds get_tests() method with automatic continuation
token handling.
```

## Pull Request Process

1. Update [CHANGELOG.md](CHANGELOG.md) with your changes
2. Ensure all tests pass: `pytest`
3. Update documentation if needed
4. Submit PR with clear description of changes
5. Respond to review feedback promptly

### PR Title Format
```
[Type]: Brief description

Types: Feature, Fix, Refactor, Docs, Tests, CI
Example: [Feature]: Add automatic pagination for ForceFrame API
```

### PR Description Template
```markdown
## Description
Brief explanation of what this PR does.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Fixes #123

## Testing
Describe how you tested these changes.

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code formatted with Black
- [ ] All tests passing
```

## Reporting Bugs

Use the [Issue Template](https://github.com/dgaytanjenkins/Valdpy/issues/new) and include:

1. **Description**: What is the bug?
2. **Expected Behavior**: What should happen?
3. **Actual Behavior**: What actually happens?
4. **Steps to Reproduce**: How can someone reproduce this?
5. **Environment**: Python version, OS, VALDPY version
6. **Error Message**: Full traceback if applicable

Example:
```markdown
## Description
API returns empty DataFrame when filtering by profile_id

## Expected Behavior
Should return DataFrame with tests for that profile

## Actual Behavior
Returns empty DataFrame with message "No data found"

## Steps to Reproduce
1. Initialize ForeDecksAPI
2. Call get_tests_info('01/01/2025', profile_id='123')
3. Observe empty result

## Environment
- Python 3.9
- VALDPY 0.1.0
- Windows 10
```

## Feature Requests

Suggest new features by [creating an issue](https://github.com/dgaytanjenkins/Valdpy/issues) with:

1. **Use Case**: Why is this feature needed?
2. **Proposed Solution**: How should it work?
3. **Alternatives**: Are there other ways to solve this?

## Documentation

Contributions to documentation are welcome:

- Fix typos and clarify explanations
- Add examples and use cases
- Improve API documentation
- Create tutorials

Documentation files:
- Main docs: `docs/*.md`
- API reference: `docs/api_reference/*.md`
- Examples: `examples/*.ipynb`

## Project Structure

```
valdpy/
├── api/                  # API client implementations
├── utils.py              # Utility functions
└── __init__.py          # Package initialization

docs/                     # Documentation
examples/                 # Jupyter notebook examples
tests/                    # Test suite

setup.py
pyproject.toml
README.md
LICENSE
```

## Questions?

- Check [FAQ](docs/faq.md)
- Open a [Discussion](https://github.com/dgaytanjenkins/Valdpy/discussions)
- Email: dgaytanj@uoregon.edu

## Recognition

All contributors will be recognized in:
- CHANGELOG.md
- README.md (Contributors section)
- GitHub contributors page

Thank you for contributing to VALDPY! 🎉
