## 2024-05-21 - XSS in HTML Generation
**Learning:** Generating HTML forms using template literals (e.g., `value="${data}"`) creates XSS vulnerabilities if the data contains quotes or scripts.
**Action:** Always create input elements and assign `value` via JavaScript properties (e.g., `input.value = data`) to handle escaping automatically.
