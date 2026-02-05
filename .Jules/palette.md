## 2024-05-23 - Legacy Frontend Cleanup & Accessibility
**Learning:** "Micro-UX" often starts with fixing broken UI. A "bad merge" left duplicate IDs and broken JS in `legacy-index.html`, making any accessibility work impossible until fixed.
**Action:** Always verify the "base state" of legacy files before applying enhancements. Use Playwright to check for duplicate IDs (`document.querySelectorAll('[id]')`) as a sanity check.

## 2024-05-23 - Modal Accessibility Pattern
**Learning:** Simple modals in legacy JS need three things to feel modern: 1) `aria-label` on close buttons, 2) Focus management (focus first input on open), 3) Escape key listener.
**Action:** Use this reusable pattern for any future vanilla JS modals in this repo:
```javascript
// On Open
modal.classList.add('active');
input.focus();

// Global Listener
document.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeModal();
});
```
