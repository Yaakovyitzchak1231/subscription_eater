# Palette's Journal

## 2024-05-22 - Accessible Modal Forms
**Learning:** Dynamic forms often miss basic accessibility associations because they are constructed as strings. Explicitly linking labels to inputs with `for`/`id` attributes is critical for screen readers, even in dynamically generated content.
**Action:** When building HTML strings for dynamic forms, always generate unique IDs and ensure `<label for="...">` matches `<input id="...">`.
