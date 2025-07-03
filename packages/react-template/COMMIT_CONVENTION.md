# Commit Message Convention

This project uses [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) for commit messages.

## Format

```
<type>(<scope>): <subject>
```

- **type**: The type of change (see allowed types below)
- **scope**: The area of the codebase affected (optional, but recommended)
- **subject**: A short description of the change

## Examples

```
feat(auth): add login endpoint
fix(ui): resolve issue with form validation on mobile
docs(readme): update API section with new auth flow
refactor(ui): simplify modal component structure
test(auth): add unit tests for login functionality
```

## Allowed types

- feat:     A new feature
- fix:      A bug fix
- docs:     Documentation only changes
- style:    Changes that do not affect the meaning of the code (white-space, formatting, etc)
- refactor: A code change that neither fixes a bug nor adds a feature
- perf:     A code change that improves performance
- test:     Adding missing tests or correcting existing tests
- build:    Changes that affect the build system or external dependencies
- ci:       Changes to CI configuration files and scripts
- chore:    Other changes that don't modify src or test files
- revert:   Reverts a previous commit

## Why?

- Enforces a readable commit history
- Enables automatic changelog generation
- Helps with code reviews and collaboration

For more details, see [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/). 