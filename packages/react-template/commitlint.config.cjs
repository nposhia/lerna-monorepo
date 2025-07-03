module.exports = {
  extends: ["@commitlint/config-conventional"],
  rules: {
    "type-enum": [
      2,
      "always",
      [
        "feat",
        "fix",
        "docs",
        "style",
        "refactor",
        "perf",
        "test",
        "build",
        "ci",
        "chore",
        "revert",
      ],
    ],
  },
  helpUrl: `\n❌ Invalid commit message format!\n\nExample: feat(auth): add login endpoint\n\nAllowed types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert\nFormat: <type>(<scope>): <subject>\n`,
}; 