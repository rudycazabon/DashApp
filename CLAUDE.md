# Project Description

The goal of this project is to create a cross-platform (Linux, Windows, and MacOS) Python textual UI (TUI) dashboard application that shall be named "DashApp." DashApp will be developed in stages. At its core, DashApp will be a plugin based such that each new tool will be added as python plugins. Throughout the development of new tools, bug fixing, packaging, and deployment cycle testing will be performed. Initially this application will be geared towards deployment on the desktop. Later, a mobile and web-client will be developed.

# Development Guidelines

This document contains critical information about working with this codebase. Follow these guidelines precisely.

## Core Development Rules

1. Package Management
   - ONLY use uv, NEVER pip
   - Installation: `uv add package`
   - Running tools: `uv run tool`
   - Upgrading: `uv add --dev package --upgrade-package package`
   - FORBIDDEN: `uv pip install`, `@latest` syntax

2. Code Quality
   - Type hints required for all code
   - Public APIs must have docstrings
   - Functions must be focused and small
   - Follow existing patterns exactly
   - Line length: 88 chars maximum

3. Testing Requirements
   - Framework: `uv run pytest`
   - Async testing: use anyio, not asyncio
   - Coverage: test edge cases and errors
   - New features require tests
   - Bug fixes require regression tests

4. Code Style
    - PEP 8 naming (snake_case for functions/variables)
    - Class names in PascalCase
    - Constants in UPPER_SNAKE_CASE
    - Document with docstrings
    - Use f-strings for formatting

## Development Philosophy

- **Simplicity**: Write simple, straightforward code
- **Readability**: Make code easy to understand
- **Performance**: Consider performance without sacrificing readability
- **Maintainability**: Write code that's easy to update
- **Testability**: Ensure code is testable
- **Reusability**: Create reusable components and functions
- **Less Code = Less Debt**: Minimize code footprint

## Coding Best Practices

- **Early Returns**: Use to avoid nested conditions
- **Descriptive Names**: Use clear variable/function names (prefix handlers with "handle")
- **Constants Over Functions**: Use constants where possible
- **DRY Code**: Don't repeat yourself
- **Functional Style**: Prefer functional, immutable approaches when not verbose
- **Minimal Changes**: Only modify code related to the task at hand
- **Function Ordering**: Define composing functions before their components
- **TODO Comments**: Mark issues in existing code with "TODO:" prefix
- **Simplicity**: Prioritize simplicity and readability over clever solutions
- **Build Iteratively** Start with minimal functionality and verify it works before adding complexity
- **Run Tests**: Test your code frequently with realistic inputs and validate outputs
- **Build Test Environments**: Create testing environments for components that are difficult to validate directly
- **Functional Code**: Use functional and stateless approaches where they improve clarity
- **Clean logic**: Keep core logic clean and push implementation details to the edges
- **File Organsiation**: Balance file organization with simplicity - use an appropriate number of files for the project scale

# Project Structure

The project structure will be as follows:

```
DashAPP/
├── .gitignore
├── README.md
├── config.py
├── tui/                      # TUI
├── tools/                    # tools (self-contained)
│   └── <toolname>/
│       ├── tool.py           # Tool implementation
│       ├── manifest.json     # tool metadata
├── util/                     # Shared utilities
├── sqlite3/                     # Shared utilities
├── pytest/                   # Shared testing
├── loader.py                 # Tool discovery and registration
└── pyproject.toml            # Dependencies
```

# System Architecture

1. Desired components: DashApp will use the python libraries textual, textual-dev, and textual[syntax] as the of the TUI interface. 
2. Tools: The main page of DashApp will present a menu of available tools to select from in a list of tabs. A tabbed page will present the content of each tool.
   1. Initial tools: As a proof-of-concept I want DashApp to build tools for my personal use. As such, security and tokens required to access my data will be asked by the application. You will install the required python packages and libraries.
      1. Presentation of email from GMail for that day
      2. Access and presentaiton of Google Calendar entries for that day.
      3. Presentation of Outlook (personal) for that day
      4. Access and presenation of Outlook calendar for that day
3. Database: It is required for DashApp to save its state between sessions. As such, a simple database like sqlite3 will be sufficient.
4. Plugin system: each tool will be a plugin. The framework will have a loader.py that performs discovery and loading of the plugins in the tools directory. Each plugin will present

## Core Components

- `config.py`: Configuration management
- `daemon.py`: Main daemon
[etc... fill in here]

## Pull Requests

- Create a detailed message of what changed. Focus on the high level description of
  the problem it tries to solve, and how it is solved. Don't go into the specifics of the
  code unless it adds clarity.

## Python Tools

## Code Formatting

1. Ruff
   - Format: `uv run ruff format .`
   - Check: `uv run ruff check .`
   - Fix: `uv run ruff check . --fix`
   - Critical issues:
     - Line length (88 chars)
     - Import sorting (I001)
     - Unused imports
   - Line wrapping:
     - Strings: use parentheses
     - Function calls: multi-line with proper indent
     - Imports: split into multiple lines

2. Type Checking
   - Tool: `uv run pyright`
   - Requirements:
     - Explicit None checks for Optional
     - Type narrowing for strings
     - Version warnings can be ignored if checks pass

3. Pre-commit
   - Config: `.pre-commit-config.yaml`
   - Runs: on git commit
   - Tools: Prettier (YAML/JSON), Ruff (Python)
   - Ruff updates:
     - Check PyPI versions
     - Update config rev
     - Commit config first

## Error Resolution

2. Common Issues
   - Line length:
     - Break strings with parentheses
     - Multi-line function calls
     - Split imports
   - Types:
     - Add None checks
     - Narrow string types
     - Match existing patterns

3. Best Practices
   - Check git status before commits
   - Run formatters before type checks
   - Keep changes minimal
   - Follow existing patterns
   - Document public APIs
   - Test thoroughly