## 2024-10-24 - Dynamic Forms Accessibility
**Learning:** The application injects form HTML via JavaScript template literals but consistently missed associating labels with inputs (using `for`/`id`) in these dynamic blocks.
**Action:** Always check `innerHTML` injections for proper label-input associations and ensure IDs are unique when generating dynamic content.
