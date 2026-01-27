## 2024-05-23 - Broken Modals & Duplicate IDs
**Learning:** Duplicate IDs in dynamically generated modal content (e.g., from copy-paste errors) can silently break accessibility and form logic, as `getElementById` only returns the first match.
**Action:** When refactoring template literals, explicitly check for duplicate ID assignments and verify logic matches the intended DOM structure.

## 2024-05-23 - Testing Local HTML with Playwright
**Learning:** Testing `file://` pages with Playwright requires `page.add_init_script` to inject environment variables (like `BACKEND_URL`) before the page loads, because `window.location.origin` is null.
**Action:** Use `add_init_script` for any environment configuration when testing static files.
