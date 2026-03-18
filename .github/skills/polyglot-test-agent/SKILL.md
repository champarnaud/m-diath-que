---
name: polyglot-test-agent
description: 'Multi-language test generation agent using a Research → Plan → Implement pipeline. Generates comprehensive unit and integration tests for Python, JavaScript, TypeScript, C#, Go, Rust, and Java.'
---

# Polyglot Test Agent

A three-phase agent pipeline for generating high-quality tests in any language.

**Triggers:** "generate tests", "write unit tests", "improve coverage", "add tests for", "test this code"

---

## Phase 1 — Research

**Goal:** Understand the code under test before writing a single line.

1. Read the target file(s) completely.
2. Identify:
   - Public API surface (functions, methods, classes, endpoints)
   - Dependencies and side effects (I/O, DB, network, time)
   - Error handling paths
   - Edge cases and boundary conditions
3. Find existing tests to understand patterns and avoid duplication.
4. Save findings to `.testagent/research.md`.

---

## Phase 2 — Plan

**Goal:** Design the test suite before writing it.

For each testable unit, plan:

| Test Name | Input | Expected Output | Type |
|-----------|-------|----------------|------|
| `test_<unit>_<scenario>` | ... | ... | unit/integration |

Categories to cover:
- Happy path (normal input → expected output)
- Boundary values (empty, zero, max, min)
- Error cases (invalid input, exceptions)
- Side effects (DB writes, external calls)

Save the plan to `.testagent/plan.md` and review before proceeding.

---

## Phase 3 — Implement

**Goal:** Write tests following language-specific best practices.

### Python / pytest

```python
import pytest
from unittest.mock import patch, MagicMock

class TestMyFunction:
    def test_returns_expected_value_for_valid_input(self):
        # Arrange
        input_data = {...}
        expected = {...}

        # Act
        result = my_function(input_data)

        # Assert
        assert result == expected

    def test_raises_value_error_for_invalid_input(self):
        with pytest.raises(ValueError, match="expected message"):
            my_function(None)

    @patch("module.external_dependency")
    def test_handles_external_failure(self, mock_dep):
        mock_dep.side_effect = ConnectionError("timeout")
        with pytest.raises(ServiceUnavailableError):
            my_function(valid_input)
```

### JavaScript / Jest

```javascript
describe('myFunction', () => {
  it('returns expected value for valid input', () => {
    // Arrange / Act / Assert
    expect(myFunction(validInput)).toEqual(expectedOutput);
  });

  it('throws for invalid input', () => {
    expect(() => myFunction(null)).toThrow('expected message');
  });
});
```

### TypeScript

Same as JavaScript; add type annotations and use `jest.spyOn` for mocking.

### C# / xUnit

```csharp
public class MyFunctionTests {
    [Fact]
    public void ReturnsExpectedValue_WhenInputIsValid() {
        // Arrange / Act / Assert
        var result = MyClass.MyFunction(validInput);
        Assert.Equal(expectedOutput, result);
    }

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    public void Throws_WhenInputIsInvalid(string input) {
        Assert.Throws<ArgumentException>(() => MyClass.MyFunction(input));
    }
}
```

### Go

```go
func TestMyFunction_ValidInput(t *testing.T) {
    result, err := MyFunction(validInput)
    if err != nil {
        t.Fatalf("unexpected error: %v", err)
    }
    if result != expected {
        t.Errorf("got %v, want %v", result, expected)
    }
}
```

---

## Naming Convention

```
test_<unit_under_test>_<expected_behavior>_when_<condition>

Examples:
  test_calculate_total_returns_zero_when_cart_is_empty
  test_create_user_raises_value_error_when_email_is_invalid
  test_fetch_data_retries_three_times_when_connection_fails
```

---

## Quality Standards

- Each test has one assertion focus (AAA pattern).
- Tests are independent — no shared mutable state.
- External dependencies (DB, API, time) are mocked.
- Test data is minimal and meaningful.
- Run the full suite after generation; all tests must pass.

---

## Output

After implementation:
1. List all generated test files.
2. Run the test suite and report results.
3. Generate a coverage report and highlight any remaining gaps.
