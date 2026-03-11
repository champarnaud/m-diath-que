---
description: 'Python coding conventions and guidelines'
applyTo: '**/*.py'
---

# Python Coding Conventions

## Langage et paradigme de développement

- Ce projet est **exclusivement écrit en Python**.
- Le développement suit le modèle **Test Driven Design (TDD)** :
  1. **Red** — Écrire d'abord un test qui échoue décrivant le comportement attendu.
  2. **Green** — Écrire le minimum de code pour faire passer ce test.
  3. **Refactor** — Améliorer le code sans changer son comportement, en s'assurant que les tests passent toujours.
- Aucune fonctionnalité ne doit être implémentée sans qu'un test ait été écrit au préalable.
- Utiliser `pytest` comme framework de test principal.
- Organiser les tests dans un dossier `tests/` à la racine du projet, en miroir de la structure du code source.
- Nommer les fichiers de test avec le préfixe `test_` (ex : `test_movie.py`).
- Nommer les fonctions de test avec le préfixe `test_` et un nom descriptif du comportement testé.

## Python Instructions

- Write clear and concise comments for each function.
- Ensure functions have descriptive names and include type hints.
- Provide docstrings following PEP 257 conventions.
- Use the `typing` module for type annotations (e.g., `List[str]`, `Dict[str, int]`).
- Break down complex functions into smaller, more manageable functions.

## General Instructions

- Always prioritize readability and clarity.
- For algorithm-related code, include explanations of the approach used.
- Write code with good maintainability practices, including comments on why certain design decisions were made.
- Handle edge cases and write clear exception handling.
- For libraries or external dependencies, mention their usage and purpose in comments.
- Use consistent naming conventions and follow language-specific best practices.
- Write concise, efficient, and idiomatic code that is also easily understandable.

## Code Style and Formatting

- Follow the **PEP 8** style guide for Python.
- Maintain proper indentation (use 4 spaces for each level of indentation).
- Ensure lines do not exceed 79 characters.
- Place function and class docstrings immediately after the `def` or `class` keyword.
- Use blank lines to separate functions, classes, and code blocks where appropriate.

## Edge Cases and Testing

- Always include test cases for critical paths of the application.
- Account for common edge cases like empty inputs, invalid data types, and large datasets.
- Include comments for edge cases and the expected behavior in those cases.
- Write unit tests for functions and document them with docstrings explaining the test cases.

## Example of Proper Documentation

```python
def calculate_area(radius: float) -> float:
    """
    Calculate the area of a circle given the radius.
    
    Parameters:
    radius (float): The radius of the circle.
    
    Returns:
    float: The area of the circle, calculated as π * radius^2.
    """
    import math
    return math.pi * radius ** 2
```
