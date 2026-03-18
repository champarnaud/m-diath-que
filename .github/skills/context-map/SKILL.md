---
name: context-map
description: 'Generate a map of all files relevant to a task before making changes. Ensures all affected code, dependencies, and tests are identified before implementation begins.'
---

# Context Map

Before implementing any changes, analyze the codebase and create a context map.

## Task

{{task_description}}

## Instructions

1. Search the codebase for files directly related to this task.
2. Identify direct dependencies (imports, exports, function calls).
3. Find related test files.
4. Look for similar patterns in existing code that should be followed.
5. Identify configuration or schema files that may need updating.

## Output Format

```markdown
## Context Map

### Files to Modify
| File | Purpose | Changes Needed |
|------|---------|----------------|
| path/to/file.py | Brief description | What needs to change |

### Dependencies (may need updates)
| File | Relationship |
|------|--------------|
| path/to/dep.py | Imports X from file to modify |

### Test Files
| Test File | Coverage Area |
|-----------|---------------|
| tests/test_x.py | Tests the module being changed |

### Reference Patterns
| File | Pattern to Follow |
|------|-------------------|
| path/to/example.py | Shows how similar feature is implemented |

### Schema / Config Changes
| File | Change Required |
|------|----------------|
| schema.sql | Add column Y to table X |

### Risk Assessment
- [ ] Breaking changes to public API
- [ ] Database migrations needed
- [ ] Configuration changes required
- [ ] Multiple consumers of modified code
- [ ] Performance implications
```

## Rules

- **Do not proceed with implementation** until this map has been reviewed.
- If a risk item is checked, describe the mitigation strategy before proceeding.
- Update the map if new dependencies are discovered during implementation.
