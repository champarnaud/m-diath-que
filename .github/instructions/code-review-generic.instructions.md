---
description: 'Generic code review instructions that can be customized for any project using GitHub Copilot'
applyTo: '**'
excludeAgent: ["coding-agent"]
---
# Generic Code Review Instructions

## Review Language

When performing a code review, respond in **English**.

## Review Priorities

- 🔴 **CRITICAL** (Block merge): Security vulnerabilities, Correctness bugs, Breaking API/contract changes, Data loss risks
- 🟡 **IMPORTANT** (Requires discussion): SOLID principle violations, Missing test coverage, Performance bottlenecks, Deviations from architecture
- 🟢 **SUGGESTION** (Non-blocking): Readability improvements, Minor optimizations, Best-practice nudges, Documentation gaps

## General Principles

1. Be specific — reference file names and line numbers.
2. Explain **why** something is an issue, not just that it is.
3. Propose solutions with corrected code snippets where possible.
4. Be constructive; acknowledge good practices explicitly.
5. Group related comments to avoid overwhelming the author.

## Code Quality Standards

- Names must be descriptive and unambiguous (variables, functions, classes, files).
- Apply the **Single Responsibility Principle** — one reason to change per unit.
- Apply **DRY** — no duplicated logic; extract shared behavior.
- Functions should be ≤ 20–30 lines; split if longer.
- Nesting depth ≤ 3–4 levels; use early returns / guard clauses.
- No magic numbers or strings — use named constants.

## Security Review

- No secrets, tokens, or passwords in code or log output.
- All user input must be validated and sanitized.
- SQL: parameterized queries / prepared statements only — no string concatenation.
- Authentication and authorization checks must precede resource access.
- Dependencies: flag known vulnerabilities (check CVE / advisory databases).

## Testing Standards

- All new or changed functionality must have corresponding tests.
- Test names must be descriptive: `should_<behavior>_when_<condition>`.
- Follow **AAA** (Arrange / Act / Assert) or **GWT** (Given / When / Then) patterns.
- Tests must be independent — no shared mutable state between tests.
- Critical code paths (happy path + error cases) must be covered.

## Performance Considerations

- Watch for N+1 query patterns; use eager loading / batch fetching.
- Cache results for expensive, frequently read, rarely changing data.
- Ensure resources (connections, file handles, streams) are properly closed.
- Paginate large data sets; never return unbounded result sets to clients.
- Evaluate algorithmic complexity for loops and data transformations.

## Documentation

- All public APIs, functions, and classes should be documented.
- Update the README when behavior, setup, or configuration changes.
- Inline comments should explain **why**, not **what** (code explains what).

## Review Checklist

- [ ] No duplicated logic; naming is clear and descriptive
- [ ] No hardcoded secrets or sensitive data in code or logs
- [ ] All user inputs are validated
- [ ] SQL uses parameterized queries
- [ ] New code has adequate test coverage
- [ ] No N+1 query patterns
- [ ] Resources are properly closed / released
- [ ] Code follows the established project patterns and architecture
- [ ] Public APIs and changed behavior are documented
- [ ] README or other docs updated if needed
