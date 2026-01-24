## 2024-05-22 - [Legacy Frontend Verification]
**Learning:** Testing legacy HTML/JS files via `file://` requires manually injecting environment variables (like `BACKEND_URL`) because `window.location.origin` is unreliable (null/file://).
**Action:** Always check for global variable overrides in legacy code and use `page.add_init_script` in Playwright to mock them for local testing.

## 2024-05-22 - [Hidden Broken State]
**Learning:** A simple "add UX" task can reveal that the underlying feature is completely broken (syntax errors, duplicate code).
**Action:** Always run a basic "does it load?" verification script before assuming the codebase is stable enough for micro-improvements.
