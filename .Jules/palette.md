## 2026-01-31 - Dynamic Form Accessibility
**Learning:** Dynamically injected form templates (via `innerHTML`) in `legacy-index.html` often miss `for`/`id` associations, breaking screen reader navigation.
**Action:** When touching JS templates, always verify label-input associations and ensure unique IDs are generated if necessary.
