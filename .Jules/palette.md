## 2025-10-26 - Accessible Tabs Pattern
**Learning:** Legacy apps often implement tabs as simple buttons with `onclick` handlers, missing critical screen reader context.
**Action:** When retrofitting tabs, always add `role="tablist"`, `role="tab"`, and `role="tabpanel"` relationships, and manage `aria-selected` state via JS.
