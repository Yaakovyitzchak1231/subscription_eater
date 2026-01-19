## 2024-05-23 - Duplicate ID Traps in Template Literals
**Learning:** Dynamic HTML generation via template literals is prone to copy-paste errors, leading to duplicate IDs (e.g., `id="edit-cost"` appearing twice). This not only breaks JS selectors but also invalidates accessibility associations (labels pointing to the wrong input).
**Action:** When auditing legacy code with template literals, always grep for IDs within the template string to ensure uniqueness.

## 2024-05-23 - Ghost UI Elements in Legacy Code
**Learning:** Legacy single-file apps often accumulate "ghost" UI elements—static placeholders (like a footer save button) that are superseded by dynamic injections but never removed. These create duplicate IDs and confusing state management.
**Action:** When working on legacy DOM manipulation, check if an element is being created dynamically AND exists statically. Prefer one source of truth.
