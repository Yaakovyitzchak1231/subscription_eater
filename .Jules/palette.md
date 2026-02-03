## 2024-10-25 - Legacy Code Duplication
**Learning:** Legacy HTML files may contain duplicate code blocks with conflicting IDs (e.g., `id="edit-cost"` appearing twice), which breaks accessibility (label associations) and JS selectors.
**Action:** checking for ID uniqueness with `grep` or verification scripts is critical when refactoring legacy views.
