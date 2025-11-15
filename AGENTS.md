# Repository Guidelines

## General Principles
- Don't over-engineer a solution when a simple one is possible. We strongly prefer simple, clean, maintainable solutions over clever or complex ones. Readability and maintainability are primary concerns, even at the cost of conciseness or performance.
- Work hard to reduce code duplication, even if the refactoring takes extra effort.

## Code Style
- 120-character lines
- Type hint is a must, even for tests and fixtures!
- **Don't use Python 3.8 typings**: Never import `List`, `Tuple` or other deprecated classes from `typing`, use `list`, `tuple` etc. instead, or import from `collections.abc`
- Do not use `from __future__ import annotations`, use forward references in type hints instead. 
- `TYPE_CHECKING` should be used only for imports that would cause circular dependencies. If you really need to use it, then you should import the submodule, not the symbol directly, and the actual usages of the imported symbols must be a fully specified forward reference string (e.g. `a.b.C` rather than just `C`.)
- Strongly prefer organizing hardcoded values as constants at the top of the file rather than scattering them throughout the code.
- Except for rarely used, heavy dependencies, always import modules at the top of the file.

### Using deal
We only use the exception handling features of deal. Use `@deal.raises` to document expected exceptions for functions/methods. Do not use preconditions/postconditions/invariants.

Additionally, we assume `AssertionError` is never raised, so `@deal.raises(AssertionError)` is not allowed.

## Documentation and Comments
Add code comments sparingly. Focus on why something is done, especially for complex logic, rather than what is done. Only add high-value comments if necessary for clarity or if requested by the user. Do not edit comments that are separate from the code you are changing. NEVER talk to the user or describe your changes through comments.

### Google-style docstrings
Use Google-style docstrings for all public or private functions, methods, classes, and modules. 

For functions (excluding FastAPI routes), always include the "Args" sections unless it has no arguments. Include "Raises" if anything is raised. Include "Returns" if it returns a complex type that is not obvious from the function signature. Optionally include an "Examples" section for complex functions.

For classes, include an "Attributes:" section if the class has attributes. Additionally, put each attribute's description in the "docstring" of the attribute itself. For dataclasses, this is a triple-quoted string right after the field definition. For normal classes, this is a triple-quoted string in either the class body or the first appearance of the attribute in the `__init__` method, depending on where the attribute is defined.

For modules, include a brief description at the top.

Additionally, for module-level constants, include a brief description right after the constant definition.

### Using a new environmental variable
When using a new environmental variable, add it to `.env.example` with a placeholder value, and optionally a comment describing its purpose. Also add it to the `Environment Variables` section in `README.md`.

## Testing Guidelines
Tests are required for all new features and bug fixes. Tests should be written using `pytest`. Even if the user does not explicitly request tests, you must add them.

Allowed pytest markers:
- builtin ones like `skip`, `xfail`, `parametrize`, etc.

### Running Tests
Use `uv run pytest ...` instead of simply `pytest ...` so that the virtual environment is activated for you.

## GitHub Actions & CI/CD
- When adding or changing GitHub Actions, always search online for the newest version and use the commit hash instead of version tags for security and immutability. (Use `gh` CLI to find the commit hash, searching won't give you helpful results.)

## Commit & Pull Requests
- Messages: imperative, concise, scoped (e.g., “Add health check endpoint”). Include extended description if necessary explaining why the change was made.

## Information
Finding dependencies: we use `pyproject.toml`, not `requirements.txt`. Use `uv add <package>` to add new dependencies.