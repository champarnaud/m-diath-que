---
name: refactor
description: 'Systematic code refactoring using proven patterns. Identifies code smells and applies targeted, behavior-preserving transformations with clear before/after examples.'
---

# Code Refactoring

## Golden Rules

1. **Behavior is preserved** — refactoring must not change observable behavior.
2. **Small, incremental steps** — one transformation at a time.
3. **Tests are essential** — run the test suite before and after each step.
4. **Commit between steps** — isolate each refactoring in its own commit.

---

## Code Smells and Transformations

### Extract Method

**Smell:** A block of code inside a function can be grouped and named.

```python
# Before
def print_bill(order):
    print(f"Order #{order.id}")
    subtotal = sum(item.price for item in order.items)
    tax = subtotal * 0.20
    total = subtotal + tax
    print(f"Total: {total:.2f}")

# After
def print_bill(order):
    print(f"Order #{order.id}")
    print(f"Total: {calculate_total(order):.2f}")

def calculate_total(order) -> float:
    subtotal = sum(item.price for item in order.items)
    return subtotal * 1.20
```

---

### Rename for Clarity

**Smell:** Names that don't reveal intent.

```python
# Before
def calc(x, lst):
    return [i for i in lst if i > x]

# After
def filter_above_threshold(threshold, values):
    return [v for v in values if v > threshold]
```

---

### Replace Magic Numbers/Strings with Named Constants

```python
# Before
if status == 2:
    send_notification()

# After
ORDER_STATUS_SHIPPED = 2

if status == ORDER_STATUS_SHIPPED:
    send_notification()
```

---

### Flatten Nested Conditionals (Guard Clauses)

**Smell:** Arrow anti-pattern — deeply nested `if`/`else`.

```python
# Before
def process(user):
    if user:
        if user.is_active:
            if user.has_permission("edit"):
                perform_edit(user)

# After
def process(user):
    if not user:
        return
    if not user.is_active:
        return
    if not user.has_permission("edit"):
        return
    perform_edit(user)
```

---

### Decompose God Object / Large Class

**Smell:** A class that knows too much or does too much.

- Identify clusters of fields and methods that belong together.
- Extract each cluster into a new, focused class.
- Delegate from the original class to the new ones.

---

### Remove Duplicated Code (DRY)

**Smell:** Same logic copy-pasted in multiple places.

- Extract the common logic into a shared function, method, or base class.
- Replace all occurrences with a call to the extracted unit.

---

### Reduce Long Parameter Lists

**Smell:** A function with > 3–4 parameters.

```python
# Before
def create_user(first_name, last_name, email, role, department, team):
    ...

# After — group related params into a data class
@dataclass
class UserData:
    first_name: str
    last_name: str
    email: str
    role: str
    department: str
    team: str

def create_user(data: UserData):
    ...
```

---

### Remove Dead Code

**Smell:** Unreachable code, commented-out blocks, unused variables/imports.

- Delete, don't comment out. Version control preserves history.
- Use linters (`flake8 F401`, `pylint`, `eslint no-unused-vars`) to detect automatically.

---

## Refactoring Workflow

```
1. Ensure all existing tests pass
2. Identify the code smell
3. Choose the appropriate transformation
4. Apply the smallest possible change
5. Run tests — must still pass
6. Commit with a message: refactor: <what was changed>
7. Repeat
```

## Output Format

For each refactoring, provide:

1. **Code smell identified** — name and location
2. **Before** — original code snippet
3. **After** — refactored code snippet
4. **Explanation** — why this is an improvement
5. **Risk** — any edge cases to verify
