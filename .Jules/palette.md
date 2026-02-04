
## 2024-05-22 - Legacy Modal XSS & A11y
**Learning:** Legacy code using `innerHTML` with template literals is a prime vector for XSS. Replacing interpolation with `textContent` and `.value` assignment is a necessary refactor step. Also, Playwright's `get_by_role("dialog")` relies on explicit `role="dialog"` attributes, which might be missing in legacy HTML.
**Action:** Audit legacy components for `innerHTML` usage and ensure proper ARIA roles are added when touching legacy HTML.
