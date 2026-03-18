---
name: git-commit
description: 'Execute git commit with conventional commit message analysis, intelligent staging, and message generation.'
license: MIT
allowed-tools: Bash
---

# Git Commit with Conventional Commits

Analyze staged/unstaged changes, generate a conventional commit message, and execute the commit.

## Commit Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, whitespace (no logic change) |
| `refactor` | Code restructure without feature or fix |
| `perf` | Performance improvement |
| `test` | Add or update tests |
| `build` | Build system or dependency changes |
| `ci` | CI/CD configuration changes |
| `chore` | Maintenance, tooling |
| `revert` | Revert a previous commit |

## Workflow

### 1. Analyze changes

```bash
git status
git diff
git diff --cached
```

### 2. Stage relevant files

Stage only files related to the logical unit of change:

```bash
git add <file1> <file2>
# or for all changes:
git add -p  # interactive, for precision
```

### 3. Generate commit message

Construct the message following this format:

```
type(scope): short imperative description

Optional body explaining WHAT changed and WHY (not HOW).
Wrap at 72 characters.

Optional footer:
BREAKING CHANGE: description
Closes #issue-number
```

**Rules:**
- Description: imperative mood, lowercase, no period, ≤ 72 chars
- Scope: optional, lowercase module or area name
- Body: separate from description with a blank line
- Breaking change: append `!` after type/scope AND add `BREAKING CHANGE:` footer

### 4. Execute

```bash
git commit -m "type(scope): description"

# For multi-line messages:
git commit -m "type(scope): description" -m "Body paragraph."

# For breaking changes:
git commit -m "feat!: new authentication API" -m "BREAKING CHANGE: token format changed from JWT to opaque."
```

## Examples

```bash
git commit -m "feat(auth): add password reset via email"
git commit -m "fix(api): return 404 when resource not found"
git commit -m "docs: add contributing guide"
git commit -m "refactor(models): extract validation into helper module"
git commit -m "test(routes): add integration tests for search endpoint"
git commit -m "chore: upgrade dependencies to latest minor versions"
```

## Safety Protocol

- **Never** use `--force` or `--force-with-lease` on shared branches.
- **Never** rewrite history on `main` or `master`.
- **Never** commit directly to a protected branch — use a PR/MR.
- Always verify `git status` is clean after committing.
