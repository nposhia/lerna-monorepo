# Husky Hooks Setup

This project uses Husky to enforce conventional commit messages and run pre-commit checks.

## Setup Instructions

### For New Developers

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd react-template
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```
   This will automatically run `husky install` due to the `prepare` script.

3. **Run the setup script (Linux/Mac)**
   ```bash
   ./setup-hooks.sh
   ```

4. **For Windows users**
   ```bash
   git config core.hooksPath .husky
   ```

### Commit Message Format

Use conventional commit format:
```
<type>(<scope>): <subject>
```

**Examples:**
- `feat(auth): add login functionality`
- `fix(ui): resolve button alignment issue`
- `docs(readme): update installation instructions`

**Allowed types:** feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert

### Troubleshooting

If hooks don't work:
1. Ensure hooks are executable: `chmod +x .husky/*`
2. Check Git hooks path: `git config --get core.hooksPath`
3. Should return `.husky`

### Requirements

- Node.js 18+
- Git
- npm or yarn 