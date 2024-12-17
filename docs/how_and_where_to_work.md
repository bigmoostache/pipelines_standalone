# How and Where to Work

This project uses a structured approach to ensure consistency and reliability.

## Directory Structure
- `src/custom_types/` contains type definitions and converters.
- `src/pipelines/` contains pipeline implementations.
- `docs/` contains documentation and guidelines.

## Workflow
- When adding a new pipeline or type, create a dedicated directory (if needed) and follow the established structure.
- Always write tests for your pipelines and types.
- Use clear naming conventions: snake_case for files and classes that match type or pipeline names in `PascalCase`.
- Commit frequently and write clear commit messages.

## Versioning and Changes
- Keep changes backward-compatible if possible.
- Update the documentation in `docs/` whenever you add new features or types.
- All new code should be properly typed and follow the code style guidelines.

## Communication
- Document assumptions and decisions in code comments or dedicated markdown files.
- When in doubt, ask or refer to existing examples within the repository.
