## 2026-02-02 - Inline Modals vs Accessibility
**Learning:** Inline modal definitions within page components (like in `Dashboard.jsx`) often lack proper focus management and semantic labelling compared to reusable modal components. This leads to `aria-label` and `htmlFor` being missed.
**Action:** When auditing pages with inline modals, explicitly check for form-label associations and close button labels, as they aren't inherited from a strict component system.
