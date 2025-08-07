# Contributing to yyprep

We welcome contributions to yyprep! This guide will help you get started with contributing to the project.

## Ways to Contribute

### 🐛 Report Bugs

Found a bug? Help us fix it by reporting it on [GitHub Issues](https://github.com/GalKepler/yyprep/issues).

**Before reporting a bug:**
- Check if the issue already exists
- Try to reproduce the bug with the latest version
- Include system information and error messages

**Bug report template:**
```markdown
## Environment
- OS: [Ubuntu 22.04 / macOS 13.0 / Windows 11]
- Python version: [3.11.0]
- yyprep version: [0.1.0]
- Docker version: [20.10.17]

## Expected Behavior
[What you expected to happen]

## Actual Behavior
[What actually happened]

## Steps to Reproduce
1. [First step]
2. [Second step]
3. [Third step]

## Error Message
```
[Complete error message]
```
```

### 💡 Suggest Features

Have an idea for a new feature? Open a [feature request](https://github.com/GalKepler/yyprep/issues/new?template=feature_request.md).

**Feature request guidelines:**
- Explain the use case clearly
- Describe the proposed solution
- Consider backward compatibility
- Provide examples if possible

### 🔧 Fix Bugs and Implement Features

Look for issues labeled with:
- `good first issue` - Great for new contributors
- `help wanted` - We need your expertise
- `bug` - Bug fixes needed
- `enhancement` - New features to implement

### 📚 Improve Documentation

Documentation contributions are highly valued:
- Fix typos and improve clarity
- Add examples and tutorials
- Expand API documentation
- Create video tutorials or blog posts

### 🧪 Add Tests

Help improve code quality by:
- Writing unit tests for new features
- Adding integration tests
- Improving test coverage
- Creating performance benchmarks

## Development Setup

### Prerequisites

- Python 3.10+
- Git
- Docker (for testing fMRIPrep integration)
- dcm2niix

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/yyprep.git
cd yyprep

# Add upstream remote
git remote add upstream https://github.com/GalKepler/yyprep.git
```

### 2. Set Up Development Environment

#### Using Conda (Recommended)

```bash
# Create development environment
conda create -n yyprep-dev python=3.11
conda activate yyprep-dev

# Install development dependencies
conda install -c conda-forge dcm2niix
pip install -e \".[test,dev,docs]\"
```

#### Using Virtual Environment

```bash
# Create virtual environment
python -m venv yyprep-dev
source yyprep-dev/bin/activate  # Linux/macOS
# yyprep-dev\\Scripts\\activate  # Windows

# Install in development mode
pip install -e \".[test,dev,docs]\"
```

### 3. Verify Installation

```bash
# Check that yyprep works
yyprep --help

# Run tests
pytest

# Check code style
pre-commit run --all-files
```

## Development Workflow

### 1. Create a Branch

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number-description
```

### 2. Make Changes

Follow these guidelines:

#### Code Style

We use several tools to maintain code quality:

```bash
# Install pre-commit hooks
pre-commit install

# Format code
black src/ tests/
isort src/ tests/

# Check style
flake8 src/ tests/
mypy src/

# Run all checks
pre-commit run --all-files
```

#### Coding Standards

- **PEP 8**: Follow Python style guidelines
- **Type hints**: Add type annotations for new functions
- **Docstrings**: Use Google-style docstrings
- **Error handling**: Include proper exception handling
- **Logging**: Use appropriate logging levels

#### Example Code Structure

```python
from pathlib import Path
from typing import List, Optional, Union

import pandas as pd
from nipype.interfaces.base import BaseInterface


def process_participants(
    participants_df: pd.DataFrame,
    bids_dir: Union[str, Path],
    heuristic: Union[str, Path],
    overwrite: bool = False,
) -> None:
    \"\"\"Process participants for DICOM to BIDS conversion.
    
    Args:
        participants_df: DataFrame with participant information
        bids_dir: Path to BIDS output directory
        heuristic: Path to heuristic file
        overwrite: Whether to overwrite existing files
        
    Raises:
        ValueError: If participants_df is empty
        FileNotFoundError: If heuristic file doesn't exist
        
    Example:
        >>> df = pd.DataFrame({'subject_id': ['001'], 'session_id': ['baseline']})
        >>> process_participants(df, '/data/bids', 'heuristic.py')
    \"\"\"
    if participants_df.empty:
        raise ValueError(\"Participants DataFrame cannot be empty\")
    
    heuristic_path = Path(heuristic)
    if not heuristic_path.exists():
        raise FileNotFoundError(f\"Heuristic file not found: {heuristic}\")
    
    # Implementation here
    pass
```

### 3. Add Tests

#### Unit Tests

Create tests in the `tests/` directory:

```python
# tests/test_new_feature.py
import pytest
import pandas as pd
from pathlib import Path

from yyprep.new_module import new_function


def test_new_function_success():
    \"\"\"Test new_function with valid input.\"\"\"
    df = pd.DataFrame({'subject_id': ['001'], 'session_id': ['baseline']})
    result = new_function(df)
    assert result is not None


def test_new_function_empty_dataframe():
    \"\"\"Test new_function raises error with empty DataFrame.\"\"\"
    df = pd.DataFrame()
    with pytest.raises(ValueError, match=\"DataFrame cannot be empty\"):
        new_function(df)


@pytest.fixture
def sample_bids_dir(tmp_path):
    \"\"\"Create a sample BIDS directory for testing.\"\"\"
    bids_dir = tmp_path / \"bids\"
    bids_dir.mkdir()
    
    # Create basic BIDS structure
    (bids_dir / \"dataset_description.json\").write_text(
        '{\"Name\": \"Test Dataset\", \"BIDSVersion\": \"1.8.0\"}'
    )
    
    return bids_dir


def test_with_bids_directory(sample_bids_dir):
    \"\"\"Test function with BIDS directory.\"\"\"
    assert sample_bids_dir.exists()
    # Test your function here
```

#### Integration Tests

Test complete workflows:

```python
# tests/test_integration.py
import pytest
from yyprep.dicom2bids.convert import convert_dicom_to_bids


@pytest.mark.integration
def test_complete_dicom2bids_workflow(sample_dicom_data, tmp_path):
    \"\"\"Test complete DICOM to BIDS conversion.\"\"\"
    # This test requires actual DICOM data
    # Skip if test data not available
    pytest.skip(\"Integration test requires DICOM data\")
```

#### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_new_feature.py

# Run with coverage
pytest --cov=yyprep

# Run only fast tests (skip integration tests)
pytest -m \"not integration\"

# Run in parallel
pytest -n auto
```

### 4. Update Documentation

#### API Documentation

Update docstrings for new functions:

```python
def new_function(param1: str, param2: Optional[int] = None) -> bool:
    \"\"\"One-line summary of the function.
    
    Longer description if needed. Explain the purpose, behavior,
    and any important details.
    
    Args:
        param1: Description of the first parameter
        param2: Description of the optional parameter
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param1 is empty
        FileNotFoundError: When required file is missing
        
    Example:
        >>> result = new_function(\"test\", 42)
        >>> print(result)
        True
        
    Note:
        Any important notes or warnings for users.
    \"\"\"
    pass
```

#### User Documentation

Update relevant documentation files:

- `docs/api.md` - Add API documentation
- `docs/usage.md` - Add usage examples
- `docs/cli.md` - Update CLI reference
- `README.md` - Update if needed

#### Building Documentation

```bash
# Install documentation dependencies
pip install -e \".[docs]\"

# Build documentation locally
cd docs/
python -m http.server 8000
# Open http://localhost:8000 in browser
```

### 5. Commit Changes

Use conventional commit messages:

```bash
# Format: type(scope): description
git commit -m \"feat(fmriprep): add support for custom output spaces\"
git commit -m \"fix(dicom2bids): handle missing session directories\"
git commit -m \"docs: add troubleshooting guide for Docker issues\"
git commit -m \"test: add integration tests for complete workflow\"
```

**Commit types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `style`: Code style changes
- `ci`: CI/CD changes
- `chore`: Maintenance tasks

### 6. Push and Create Pull Request

```bash
# Push your branch
git push origin feature/your-feature-name

# Create pull request on GitHub
# Include description, link to issues, and testing notes
```

## Pull Request Guidelines

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Related Issues
Closes #123

## Testing
- [ ] New tests added
- [ ] All tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings introduced
```

### Review Process

1. **Automated checks**: CI/CD runs tests and style checks
2. **Code review**: Maintainers review your code
3. **Feedback**: Address any requested changes
4. **Approval**: Once approved, your PR will be merged

### What We Look For

- **Functionality**: Does the code work as intended?
- **Code quality**: Is the code clean and well-structured?
- **Tests**: Are there adequate tests for the changes?
- **Documentation**: Is the change properly documented?
- **Backward compatibility**: Does it break existing functionality?

## Development Guidelines

### Project Structure

```
yyprep/
├── src/yyprep/           # Main package
│   ├── __init__.py
│   ├── cli.py            # Command-line interface
│   ├── utils.py          # Utility functions
│   ├── dicom2bids/       # DICOM to BIDS conversion
│   └── fmriprep/         # fMRIPrep integration
├── tests/                # Test suite
│   ├── __init__.py
│   ├── test_cli.py
│   └── test_*.py
├── docs/                 # Documentation
├── examples/             # Example scripts
└── pyproject.toml        # Project configuration
```

### Adding New Modules

When adding a new module:

1. Create the module in appropriate subdirectory
2. Add `__init__.py` if creating new package
3. Update imports in parent `__init__.py`
4. Add corresponding tests in `tests/`
5. Update documentation

### Error Handling

Use appropriate exception handling:

```python
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def process_file(file_path: Path) -> None:
    \"\"\"Process a file with proper error handling.\"\"\"
    try:
        if not file_path.exists():
            raise FileNotFoundError(f\"File not found: {file_path}\")
        
        # Process file
        logger.info(f\"Processing {file_path}\")
        
    except FileNotFoundError:
        logger.error(f\"File not found: {file_path}\")
        raise
    except PermissionError:
        logger.error(f\"Permission denied: {file_path}\")
        raise
    except Exception as e:
        logger.error(f\"Unexpected error processing {file_path}: {e}\")
        raise
```

### Logging

Use consistent logging throughout:

```python
import logging

# Module-level logger
logger = logging.getLogger(__name__)


def my_function():
    logger.debug(\"Detailed debug information\")
    logger.info(\"General information\")
    logger.warning(\"Warning message\")
    logger.error(\"Error occurred\")
```

## Release Process

### Version Management

We use semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Creating a Release

1. Update version in `pyproject.toml`
2. Update `HISTORY.md` with changelog
3. Create release PR
4. Tag release after merge
5. GitHub Actions handles PyPI deployment

## Community

### Getting Help

- **Discussions**: Use [GitHub Discussions](https://github.com/GalKepler/yyprep/discussions)
- **Issues**: Report bugs or request features
- **Chat**: Join our community discussions

### Code of Conduct

Please read and follow our [Code of Conduct](../CODE_OF_CONDUCT.md).

## Recognition

Contributors are recognized in:
- `AUTHORS.md` file
- Release notes
- GitHub contributor graphs
- Documentation acknowledgments

Thank you for contributing to yyprep! 🎉
