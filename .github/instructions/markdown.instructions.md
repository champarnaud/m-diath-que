---
description: 'Documentation and content creation standards'
applyTo: '**/*.md'
---
## Markdown Content Rules

1. **Headings**: Use H2 (`##`) and H3 (`###`) to structure content. Do not use H1 (`#`) — it is generated from the page or document title.
2. **Lists**: Use bullet points or numbered lists with proper indentation for nested items.
3. **Code Blocks**: Use fenced code blocks (triple backticks) with the language identifier specified.
4. **Links**: Use valid markdown link syntax `[text](url)` — no bare URLs in body text.
5. **Images**: Always include descriptive alt text `![alt text](url)`.
6. **Tables**: Use proper pipe-and-dash formatting; align columns consistently.
7. **Line Length**: Limit lines to 400 characters maximum.
8. **Whitespace**: Use a single blank line to separate sections and block elements.

## Formatting and Structure

- Use `##` for top-level sections, `###` for sub-sections — maintain a strict hierarchy.
- Use `-` for unordered lists; use `1.` for ordered lists; indent nested lists with two spaces.
- Use triple backticks with language tag for all code blocks:

  ````markdown
  ```python
  def hello():
      print("Hello, world!")
  ```
  ````

- Break prose lines at ~80 characters for readability in raw diffs.
- Use blank lines to separate headings, paragraphs, lists, and code blocks.
- Use `**bold**` for emphasis on key terms; use `_italic_` sparingly.
- Use `> blockquote` for callouts, notes, or quoted content.

## File Organization

- Start every document with a brief introductory sentence or paragraph before the first heading.
- End documents with a summary, next steps, or related links section where appropriate.
- Use consistent file naming: lowercase, words separated by hyphens (e.g., `getting-started.md`).

## Accessibility

- Every image must have meaningful alt text (or empty `alt=""` for decorative images).
- Table headers (`| Header |`) must be present; do not use tables for layout.
- Avoid using raw HTML in Markdown unless strictly necessary.

## Links and References

- Prefer relative links for documents within the same repository.
- Verify all links are valid before committing.
- Use reference-style links for URLs that appear multiple times.
