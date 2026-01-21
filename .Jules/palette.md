## 2024-05-22 - Modal Accessibility Pattern
**Learning:** Legacy modals in this codebase rely on `innerHTML` injection, which makes keeping ARIA attributes and event listeners tricky. They consistently lacked `role="dialog"`, `aria-modal="true"`, and focus management.
**Action:** When refactoring legacy modals, always wrap the container with `role="dialog"` and `aria-modal="true"`, and ensure focus is programmatically moved to the first input after injection using `setTimeout` to allow for rendering.

## 2024-05-22 - Secure HTML Injection
**Learning:** Legacy code using `innerHTML` templates must never interpolate user values directly into attributes (e.g., `value="${input}"`) to avoid XSS.
**Action:** Always render empty inputs in the template string and use `document.getElementById('id').value = input` to assign values safely.
