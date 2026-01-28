## 2024-05-23 - Modal Usability & XSS Safety
**Learning:** Modals with long content can push action buttons (like "Save") out of the viewport if the entire modal scrolls. Users may not realize they need to scroll to find the action.
**Action:** Use `display: flex; flex-direction: column` on the modal container and `overflow-y: auto` only on the content body to create a sticky footer for actions.

**Learning:** Injecting user data into HTML strings via template literals is a common XSS vector in legacy apps.
**Action:** Always use `element.value = data` for inputs instead of `value="${data}"`, and use an `escapeHtml` helper for text content.
