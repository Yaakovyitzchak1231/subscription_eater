import os
from playwright.sync_api import sync_playwright, expect

def verify_accessibility_and_ux(page):
    # Load the local HTML file
    file_path = os.path.abspath("legacy-index.html")
    page.goto(f"file://{file_path}")

    # 1. Verify Theme Toggle Accessibility
    theme_btn = page.locator("#theme-toggle")

    # Check initial state (should be dark mode by default if system pref matches or no pref, but script defaults to dark if localstorage says so)
    # Actually, the script checks localStorage. If null, it doesn't add dark-mode class.
    # But let's check the aria-label logic.

    # Click it to ensure label changes
    initial_label = theme_btn.get_attribute("aria-label")
    print(f"Initial theme toggle label: {initial_label}")

    theme_btn.click()
    new_label = theme_btn.get_attribute("aria-label")
    print(f"New theme toggle label: {new_label}")

    assert initial_label != new_label, "Theme toggle aria-label should change"
    assert "Switch to" in new_label, "Theme toggle label should be descriptive"

    # 2. Verify Modal Accessibility
    # We need to trigger the modal. We can mock subscriptions data or inject it.
    # Since we loaded via file://, fetch won't work for /subscriptions.
    # We can inject data into the `subscriptions` variable and call `showEmailDetails`.

    page.evaluate("""
        subscriptions = [{
            id: 1,
            service_name: "Netflix",
            cost: 15.99,
            currency: "USD",
            billing_cycle: "monthly",
            category: "Entertainment",
            status: "active",
            source_email_from: "info@netflix.com",
            source_email_subject: "Your receipt",
            confidence_score: 0.95
        }];
        showEmailDetails(1);
    """)

    modal = page.locator("#email-modal")
    expect(modal).to_be_visible()
    expect(modal).to_have_attribute("role", "dialog")
    expect(modal).to_have_attribute("aria-modal", "true")
    expect(modal).to_have_attribute("aria-labelledby", "modal-title")

    # Verify Close Button
    close_btn = modal.locator(".modal-close")
    expect(close_btn).to_have_attribute("aria-label", "Close modal")

    # Verify Form Labels
    # Check if 'Service Name' label is associated with input
    service_label = modal.locator("label[for='edit-service-display']")
    expect(service_label).to_be_visible()
    expect(service_label).to_have_text("Service Name")

    service_input = modal.locator("#edit-service-display")
    expect(service_input).to_be_visible()
    expect(service_input).to_be_disabled()

    # Take screenshot
    page.screenshot(path="verification/accessibility_check.png")
    print("Screenshot saved to verification/accessibility_check.png")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            verify_accessibility_and_ux(page)
        except Exception as e:
            print(f"Verification failed: {e}")
            exit(1)
        finally:
            browser.close()
