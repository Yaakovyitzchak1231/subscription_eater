## 2024-05-22 - Fixing Broken Frontend Code
**Learning:** Copy-paste errors in frontend templates can silently break the entire application if not linted or compiled. The presence of duplicate functions and syntax errors in `index.html` highlights the fragility of raw HTML/JS without a build step.
**Action:** When working with single-file HTML apps, be extra vigilant about function closures and template literal contents. Use visual inspection or a linter if possible.
