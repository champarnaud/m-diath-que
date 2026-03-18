---
description: 'Automatically update README.md and documentation files when application code changes require documentation updates'
applyTo: '**/*.{md,py,html,css,sql}'
---
# Update Documentation on Code Change

## Overview

Ensure documentation stays synchronized with code changes by automatically detecting when README.md, API documentation, configuration guides, and other documentation files need updates based on code modifications.

## When to Update Documentation

### Trigger Conditions

Automatically check if documentation updates are needed when:

- New features or functionality are added
- API endpoints, methods, or interfaces change
- Breaking changes are introduced
- Dependencies or requirements change
- Configuration options or environment variables are modified
- Installation or setup procedures change
- Command-line interfaces or scripts are updated
- Code examples in documentation become outdated

## Documentation Update Rules

### README.md Updates

**Always update README.md when:**

- Adding new features or capabilities
  - Add feature description to "Features" section
  - Include usage examples if applicable
  - Update table of contents if present

- Modifying installation or setup process
  - Update "Installation" or "Getting Started" section
  - Revise dependency requirements
  - Update prerequisite lists

- Adding new CLI commands or options
  - Document command syntax and examples
  - Include option descriptions and default values
  - Add usage examples

- Changing configuration options
  - Update configuration examples
  - Document new environment variables
  - Update config file templates

### Code Example Synchronization

**Verify and update code examples when:**

- Function signatures change
  - Update all code snippets using the function
  - Verify examples still compile/run
  - Update import statements if needed

- API interfaces change
  - Update example requests and responses
  - Revise client code examples

### Migration and Breaking Changes

**Create migration guides when:**

- Breaking API changes occur
  - Document what changed
  - Provide before/after examples
  - Include step-by-step migration instructions

- Major version updates
  - List all breaking changes
  - Provide upgrade checklist

## Best Practices

- ✅ Update documentation in the same commit as code changes
- ✅ Include before/after examples for changes to be reviewed before applying
- ✅ Test code examples before committing
- ✅ Use consistent formatting and terminology
- ✅ Document limitations and edge cases
- ✅ Provide migration paths for breaking changes
- ❌ Commit code changes without updating documentation
- ❌ Leave outdated examples in documentation
- ❌ Forget to update changelog

## Review Checklist

Before considering documentation complete:

- [ ] README.md reflects current project state
- [ ] All new features are documented
- [ ] Code examples are tested and work
- [ ] Configuration examples are up to date
- [ ] Breaking changes are documented with migration guide
- [ ] Installation instructions are current
