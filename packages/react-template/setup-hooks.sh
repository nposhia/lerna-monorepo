#!/bin/bash

# Setup script for Husky hooks
echo "Setting up Husky hooks..."

# Configure Git to use .husky directory for hooks
git config core.hooksPath .husky

# Ensure hooks are executable
chmod +x .husky/pre-commit
chmod +x .husky/commit-msg

# Fix line endings for cross-platform compatibility
sed -i 's/\r$//' .husky/pre-commit
sed -i 's/\r$//' .husky/commit-msg

echo "✅ Husky hooks setup complete!"
echo "You can now commit with conventional commit messages." 