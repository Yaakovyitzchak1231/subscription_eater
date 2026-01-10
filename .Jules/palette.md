## 2024-05-22 - Accessible Tabs
**Learning:** Retrofitting accessibility onto `div`/`button` based tabs requires not just roles but careful management of `aria-selected` vs active classes.
**Action:** When implementing tabs, always use `role="tablist"` on container and `aria-controls` on buttons to ensure screen readers understand the relationship.
