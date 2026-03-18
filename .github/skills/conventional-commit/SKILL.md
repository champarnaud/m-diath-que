---
name: conventional-commit
description: 'Prompt and workflow for generating conventional commit messages using a structured XML format. Guides users to create standardized, descriptive commit messages in line with the Conventional Commits specification, including instructions, examples, and validation.'
---

### Instructions

Workflow for generating conventional commit messages following the [Conventional Commits](https://www.conventionalcommits.org/) specification.

### Workflow

1. Run `git status` to review the list of changed files.
2. Run `git diff` or `git diff --cached` to inspect the actual changes.
3. Stage your changes with `git add <file>`.
4. Construct your commit message using the XML structure below.
5. After generating your commit message, run:

```bash
git commit -m "type(scope): description"
```

### Commit Message Structure

```xml
<commit-message>
  <type>feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert</type>
  <scope>(optional module or area affected)</scope>
  <description>A short, imperative summary of the change</description>
  <body>(optional: more detailed explanation of what and why)</body>
  <footer>(optional: e.g. BREAKING CHANGE: details, or Closes #123)</footer>
</commit-message>
```

### Type Reference

| Type | When to use |
|------|-------------|
| `feat` | A new feature |
| `fix` | A bug fix |
| `docs` | Documentation only changes |
| `style` | Formatting, missing semicolons, etc. (no logic change) |
| `refactor` | Code change that is not a bug fix nor a feature |
| `perf` | Performance improvement |
| `test` | Adding or updating tests |
| `build` | Changes to build system or dependencies |
| `ci` | Changes to CI/CD configuration |
| `chore` | Routine maintenance, tooling |
| `revert` | Reverts a previous commit |

### Examples

```
feat(auth): add OAuth2 login with GitHub
fix(api): handle null response from external service
docs: update README with deployment instructions
refactor(models): extract validation logic into helper
feat!: redesign user API (BREAKING CHANGE: response shape changed)
```

### Validation

- **Type**: Must be one of the allowed types listed above.
- **Scope**: Optional, but recommended for clarity. Use lowercase, no spaces.
- **Description**: Required. Use imperative mood — "add", not "added" or "adds". Max 72 characters.
- **Body**: Optional. Separate from description with a blank line. Explain *why*, not *what*.
- **Footer**: Use for breaking changes (`BREAKING CHANGE: ...`) or issue references (`Closes #123`).
