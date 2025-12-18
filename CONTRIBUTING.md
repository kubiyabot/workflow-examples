# Contributing to workflow-examples

Thank you for your interest in contributing to workflow-examples! This document provides guidelines for contributing to this Python workflow examples repository.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/workflow-examples.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes
6. Commit and push your changes
7. Open a Pull Request

## Development Setup

### Prerequisites

- Python 3.13 or higher
- pip or uv package manager

### Installation

Install dependencies:

```bash
pip install -r requirements.txt
```

Or with uv:

```bash
uv sync
```

## Code Standards

### Python Style Guide

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use type hints where applicable
- Write docstrings for functions, classes, and modules
- Keep functions focused and modular

### Code Quality Tools

We use the following tools to maintain code quality:

- **ruff**: For linting and formatting
- **flake8**: For additional style checking

Run linting before committing:

```bash
ruff check .
flake8 .
```

Format code with ruff:

```bash
ruff format .
```

## Workflow Examples Guidelines

When adding new workflow examples:

1. **Structure**: Place workflows in the `workflows/` directory
2. **Documentation**: Include clear docstrings explaining the workflow purpose
3. **Message Blocks**: Use Pydantic models for message blocks (see `message_blocks/`)
4. **Models**: Define data models in the `models/` directory
5. **Testing**: Add example usage or test cases
6. **Documentation**: Update the docs in the `docs/` directory

### Example Workflow Structure

```python
from kubiya_workflow_sdk import Workflow
from pydantic import BaseModel

class WorkflowInput(BaseModel):
    """Input model for the workflow."""
    parameter: str

def create_example_workflow() -> Workflow:
    """
    Create an example workflow.

    Returns:
        Workflow: Configured workflow instance
    """
    # Implementation here
    pass
```

## Commit Messages

Write clear, descriptive commit messages:

- Use the imperative mood ("Add feature" not "Added feature")
- Keep the first line under 50 characters
- Add a blank line before detailed description
- Reference issues and pull requests when applicable

Example:

```
Add incident escalation workflow

- Implement escalation logic
- Add notification message blocks
- Update documentation

Fixes #123
```

## Pull Request Process

1. **Update Documentation**: Ensure the README.md and docs are updated
2. **Add Examples**: Include usage examples for new workflows
3. **Test Your Changes**: Verify workflows execute correctly
4. **Describe Changes**: Provide a clear description in the PR
5. **Link Issues**: Reference any related issues

### PR Checklist

- [ ] Code follows the project style guidelines
- [ ] Documentation has been updated
- [ ] Examples are included for new workflows
- [ ] Commit messages are clear and descriptive
- [ ] All checks pass (linting, formatting)

## Testing

Test your workflows locally:

```python
from kubiya_workflow_sdk import KubiyaClient
from workflows import your_workflow

wf = your_workflow.create_workflow()
client = KubiyaClient(api_key="test_key", runner="test_runner")

# Test workflow execution
result = client.execute_workflow(wf.to_dict())
```

## Documentation

Update documentation when:

- Adding new workflows
- Changing existing workflow behavior
- Adding new message blocks or models
- Modifying the API

Documentation files are located in the `docs/` directory.

## Questions?

If you have questions or need help:

1. Check existing [Issues](https://github.com/kubiyabot/workflow-examples/issues)
2. Open a new issue with the `question` label
3. Reach out to the maintainers

## Code of Conduct

Please note that this project has a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (see [LICENSE](LICENSE)).
