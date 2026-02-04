import re

def verify_html(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    print(f"Scanning {filepath}...")
    errors = []

    # 1. Check for Duplicate IDs (edit-cost)
    cost_id_count = content.count('id="edit-cost"')
    if cost_id_count > 1:
        errors.append(f"Duplicate ID found: edit-cost (count: {cost_id_count})")

    # 2. Check for missing aria-labels
    if 'class="modal-close" onclick="closeModal()">&times;' in content and \
       'aria-label=' not in re.search(r'class="modal-close"[^>]*>', content).group(0):
        errors.append("Missing aria-label on modal-close button")

    if 'id="theme-toggle"' in content and 'aria-label=' not in re.search(r'id="theme-toggle"[^>]*>', content).group(0):
        errors.append("Missing aria-label on theme-toggle button")

    # 3. Check for labels without 'for' attribute
    # We look for <label>Cost</label> which we know exists and shouldn't
    if re.search(r'<label>\s*Cost\s*</label>', content):
        errors.append("Found label without 'for' attribute: Cost")

    if re.search(r'<label>\s*Billing Cycle\s*</label>', content):
        errors.append("Found label without 'for' attribute: Billing Cycle")

    if errors:
        print("❌ Verification Failed:")
        for e in errors:
            print(f"  - {e}")
    else:
        print("✅ Verification Passed!")

if __name__ == "__main__":
    verify_html("legacy-index.html")
